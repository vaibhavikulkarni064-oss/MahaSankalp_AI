import hashlib, os, secrets, sqlite3
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from backend import database, career_engine
from backend.schemas import AssessmentIn

COOKIE = "mc_session"
PROD = os.environ.get("MAHACAREER_PROD") == "1"

@asynccontextmanager
async def lifespan(app):
    database.init_db()
    yield

app = FastAPI(title="MahaCareer AI", version="1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://127.0.0.1:8000", "http://localhost:8000", "http://127.0.0.1:5500", "http://localhost:5500"],
                   allow_credentials=True, allow_methods=["GET", "POST", "DELETE"], allow_headers=["Content-Type"])

def _hash(tok): return hashlib.sha256(tok.encode()).hexdigest()
def _session(req):
    t = req.cookies.get(COOKIE)
    return _hash(t) if t else None

@app.exception_handler(sqlite3.Error)
async def db_error(request, exc):
    return JSONResponse(status_code=500, content={"detail": "A database error occurred. Your report was not saved. Please retry."})

@app.get("/health")
def health(): return {"status": "ok"}

@app.get("/careers")
def careers():
    keys = ("career_name","description","required_skills","recommended_learning_topics","education_guidance","project_ideas")
    return [{k: c[k] for k in keys} for c in database.get_catalogue()]

@app.post("/analyze", status_code=201)
def analyze(data: AssessmentIn, request: Request, response: Response):
    token = request.cookies.get(COOKIE) or secrets.token_urlsafe(32)
    a = data.model_dump()
    report = career_engine.analyze(a, database.get_catalogue())
    database.save_report(_hash(token), a, report)   # raises -> 500; never returns fake success
    response.set_cookie(COOKIE, token, httponly=True, samesite="lax", secure=PROD, max_age=60*60*24*180)
    return report

@app.get("/assessments")
def assessments(request: Request):
    s = _session(request)
    return database.list_reports(s) if s else []

@app.get("/assessments/{assessment_id}")
def assessment(assessment_id: int, request: Request):
    s = _session(request)
    r = database.get_report(assessment_id, s) if s else None
    if not r: raise HTTPException(404, "Report not found.")
    return r

@app.delete("/assessments/{assessment_id}")
def delete_one(assessment_id: int, request: Request):
    s = _session(request)
    if not s or not database.delete_reports(s, assessment_id): raise HTTPException(404, "Report not found.")
    return {"deleted": 1}

@app.delete("/assessments")
def delete_all(request: Request):
    s = _session(request)
    return {"deleted": database.delete_reports(s) if s else 0}

app.mount("/", StaticFiles(directory=Path(__file__).resolve().parent.parent / "frontend", html=True), name="frontend")
