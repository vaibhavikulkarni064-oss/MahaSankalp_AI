import json, os, sqlite3
from contextlib import contextmanager
from backend.catalogue import CAREERS

DB_PATH = os.environ.get("MAHACAREER_DB", os.path.join(os.path.dirname(__file__), "..", "database", "career_assessments.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE,
  password_hash TEXT, created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')));
CREATE TABLE IF NOT EXISTS assessments(id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, session_hash TEXT,
  name TEXT NOT NULL, age_range TEXT NOT NULL, education_level TEXT NOT NULL, field_of_study TEXT NOT NULL,
  favourite_subjects TEXT NOT NULL, interests TEXT NOT NULL, existing_skills TEXT NOT NULL, desired_skills TEXT NOT NULL,
  work_style TEXT NOT NULL, career_goals TEXT NOT NULL, industries TEXT NOT NULL, experience TEXT,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
  CHECK(user_id IS NOT NULL OR session_hash IS NOT NULL));
CREATE INDEX IF NOT EXISTS idx_assess_session ON assessments(session_hash);
CREATE TABLE IF NOT EXISTS career_recommendations(id INTEGER PRIMARY KEY AUTOINCREMENT,
  assessment_id INTEGER NOT NULL UNIQUE REFERENCES assessments(id) ON DELETE CASCADE,
  recommended_career TEXT NOT NULL, alternative_careers TEXT NOT NULL,
  suitability_score INTEGER NOT NULL CHECK(suitability_score BETWEEN 0 AND 100),
  explanation TEXT NOT NULL, skills_to_improve TEXT NOT NULL, learning_roadmap TEXT NOT NULL, report_json TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')));
CREATE TABLE IF NOT EXISTS career_catalogue(id INTEGER PRIMARY KEY AUTOINCREMENT, career_name TEXT NOT NULL UNIQUE,
  description TEXT NOT NULL, required_skills TEXT NOT NULL, recommended_learning_topics TEXT NOT NULL,
  education_guidance TEXT NOT NULL, project_ideas TEXT NOT NULL, keywords TEXT NOT NULL);
"""

@contextmanager
def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)
    with connect() as c:
        c.executescript(SCHEMA)
        for n, d, s, t, e, p, k in CAREERS:
            c.execute("INSERT OR IGNORE INTO career_catalogue(career_name,description,required_skills,recommended_learning_topics,education_guidance,project_ideas,keywords) VALUES(?,?,?,?,?,?,?)",
                      (n, d, json.dumps(s), json.dumps(t), e, json.dumps(p), json.dumps(k)))

def _row(r):
    d = dict(r)
    for k in ("required_skills","recommended_learning_topics","project_ideas","keywords"):
        if k in d: d[k] = json.loads(d[k])
    return d

def get_catalogue():
    with connect() as c:
        return [_row(r) for r in c.execute("SELECT * FROM career_catalogue ORDER BY id")]

def save_report(session_hash, a, report):
    """Saves assessment + recommendation in ONE transaction; returns (id, created_at)."""
    J = json.dumps
    with connect() as c:
        cur = c.execute("""INSERT INTO assessments(session_hash,name,age_range,education_level,field_of_study,favourite_subjects,
            interests,existing_skills,desired_skills,work_style,career_goals,industries,experience) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (session_hash, a["name"], a["age_range"], a["education_level"], a["field_of_study"], J(a["favourite_subjects"]),
             J(a["interests"]), J(a["existing_skills"]), J(a["desired_skills"]), a["work_style"], a["career_goals"], J(a["industries"]), a.get("experience")))
        aid = cur.lastrowid
        rec = report["recommended"]
        report["id"] = aid
        report["created_at"] = c.execute("SELECT created_at FROM assessments WHERE id=?", (aid,)).fetchone()[0]
        c.execute("INSERT INTO career_recommendations(assessment_id,recommended_career,alternative_careers,suitability_score,explanation,skills_to_improve,learning_roadmap,report_json) VALUES(?,?,?,?,?,?,?,?)",
                  (aid, rec["career"], J(report["alternatives"]), rec["score"], rec["explanation"], J(rec["skills_to_improve"]), J(report["roadmap"]), J(report)))
    return aid, report["created_at"]

def get_report(aid, session_hash):
    with connect() as c:
        r = c.execute("""SELECT r.report_json FROM career_recommendations r JOIN assessments a ON a.id=r.assessment_id
                         WHERE a.id=? AND a.session_hash=?""", (aid, session_hash)).fetchone()
    return json.loads(r[0]) if r else None

def list_reports(session_hash):
    with connect() as c:
        rows = c.execute("""SELECT a.id,a.name,a.created_at,r.recommended_career,r.suitability_score FROM assessments a
            JOIN career_recommendations r ON r.assessment_id=a.id WHERE a.session_hash=? ORDER BY a.id DESC""", (session_hash,))
        return [dict(x) for x in rows]

def delete_reports(session_hash, aid=None):
    with connect() as c:
        if aid is None:
            return c.execute("DELETE FROM assessments WHERE session_hash=?", (session_hash,)).rowcount
        return c.execute("DELETE FROM assessments WHERE id=? AND session_hash=?", (aid, session_hash)).rowcount
