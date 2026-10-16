"""Run from project root: pytest -v   (covers engine, database and API; each test uses a fresh temp DB)"""
import json, sqlite3, pytest
from fastapi.testclient import TestClient
from backend import database, career_engine
from backend.main import app

VALID = {"name": "Asha Patil", "age_range": "18-21", "education_level": "Undergraduate", "field_of_study": "Computer Science",
         "favourite_subjects": ["Mathematics"], "interests": ["Programming", "Artificial intelligence"], "existing_skills": ["Python"],
         "desired_skills": ["SQL"], "work_style": "Independent", "career_goals": "I want to build intelligent software.", "industries": ["Technology"], "experience": None}

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", str(tmp_path / "t.db"))
    with TestClient(app) as c:
        yield c

# --- engine
def test_engine_ranks_relevant_career_first():
    r = career_engine.analyze({**VALID, "favourite_subjects": [], "experience": ""}, _cat())
    assert r["recommended"]["career"] in ("AI and Machine Learning Engineer", "Software Developer")
    assert len(r["alternatives"]) == 3 and len(r["roadmap"]) == 4 and 0 <= r["recommended"]["score"] <= 95
def test_engine_no_match_gives_zero_score_and_honest_text():
    a = {**VALID, "interests": ["Cooking"], "existing_skills": [], "desired_skills": [], "industries": [], "career_goals": "Something different.", "field_of_study": "Culinary", "favourite_subjects": []}
    r = career_engine.analyze(a, _cat()); assert r["recommended"]["score"] == 0 and "None of your answers" in r["recommended"]["explanation"]
def _cat():
    database.DB_PATH = ":memory:"  # placeholder; real catalogue below
    from backend.catalogue import CAREERS
    return [dict(id=i, career_name=n, description=d, required_skills=s, recommended_learning_topics=t, education_guidance=e, project_ideas=p, keywords=k) for i, (n, d, s, t, e, p, k) in enumerate(CAREERS, 1)]

# --- API
def test_health(client): assert client.get("/health").json() == {"status": "ok"}
def test_careers_seeded(client): assert len(client.get("/careers").json()) >= 10
def test_analyze_saves_and_retrieves(client):
    r = client.post("/analyze", json=VALID); assert r.status_code == 201
    rep = r.json(); assert rep["id"] and rep["recommended"]["career"]
    con = sqlite3.connect(database.DB_PATH)
    assert con.execute("SELECT COUNT(*) FROM assessments").fetchone()[0] == 1
    assert con.execute("SELECT recommended_career FROM career_recommendations").fetchone()[0] == rep["recommended"]["career"]
    assert client.get(f"/assessments/{rep['id']}").json()["recommended"] == rep["recommended"]
    assert len(client.get("/assessments").json()) == 1
def test_invalid_submissions_rejected(client):
    for bad in ({**VALID, "name": ""}, {**VALID, "interests": []}, {**VALID, "career_goals": "short"}, {**VALID, "age_range": "5"}, {**VALID, "name": "<script>x</script>"}):
        assert client.post("/analyze", json=bad).status_code == 422
    assert client.get("/assessments").json() == []
def test_unknown_id_404(client): assert client.get("/assessments/999").status_code == 404
def test_access_control_between_sessions(client):
    aid = client.post("/analyze", json=VALID).json()["id"]
    with TestClient(app) as other:
        assert other.get(f"/assessments/{aid}").status_code == 404
        assert other.get("/assessments").json() == [] and other.delete(f"/assessments/{aid}").status_code == 404
def test_delete_history(client):
    aid = client.post("/analyze", json=VALID).json()["id"]
    assert client.delete(f"/assessments/{aid}").status_code == 200 and client.get(f"/assessments/{aid}").status_code == 404
def test_persistence_after_restart(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", str(tmp_path / "p.db"))
    with TestClient(app) as c1:
        aid = c1.post("/analyze", json=VALID).json()["id"]; cookies = dict(c1.cookies)
    with TestClient(app, cookies=cookies) as c2:   # new app lifecycle, same DB file
        assert c2.get(f"/assessments/{aid}").status_code == 200
def test_backend_failure_returns_500_not_success(client, monkeypatch):
    def boom(*a, **k): raise sqlite3.OperationalError("disk full")
    monkeypatch.setattr(database, "save_report", boom)
    c = TestClient(app, raise_server_exceptions=False); r = c.post("/analyze", json=VALID)
    assert r.status_code == 500 and "not saved" in r.json()["detail"]
def test_foreign_keys_enforced(client):
    with database.connect() as c:
        with pytest.raises(sqlite3.IntegrityError):
            c.execute("INSERT INTO career_recommendations(assessment_id,recommended_career,alternative_careers,suitability_score,explanation,skills_to_improve,learning_roadmap,report_json) VALUES(999,'x','[]',1,'x','[]','[]','{}')")
