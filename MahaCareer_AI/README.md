# MahaCareer AI
*Discover Your Strengths. Explore Your Future.*  Rule-based career guidance (not machine learning) with FastAPI, SQLite and plain HTML/CSS/JS.

## Setup (Windows + VS Code)
1. Install Python 3.10+ from python.org (tick **Add Python to PATH**). Open the project folder in VS Code, then **Terminal > New Terminal** (PowerShell).
2. Create and activate a virtual environment:
```
python -m venv .venv
.venv\Scripts\activate
```
(If PowerShell blocks it: `Set-ExecutionPolicy -Scope Process Bypass`, then activate again.)
3. Install dependencies: `pip install -r requirements.txt`
4. (Optional) create the database now: `python -m database.init_db` (it is also created automatically at startup).
5. Start the server: `uvicorn backend.main:app --reload`
6. Open **http://127.0.0.1:8000** - the backend serves the website, so no separate frontend server is needed. API docs: http://127.0.0.1:8000/docs
   (If you prefer VS Code Live Server on port 5500, that origin is allowed by CORS, but cookies work best on 8000.)

## Verify that a report is saved
1. Complete the assessment on the site and click **Analyze my profile**. The report shows an ID.
2. Open **My Reports**: your report is listed; click **Open** to reload it from the database.
3. Stop the server (Ctrl+C), start it again, reload My Reports: the report is still there.
4. Optional: `python -c "import sqlite3;print(sqlite3.connect('database/career_assessments.db').execute('select id,name,recommended_career from assessments a join career_recommendations r on r.assessment_id=a.id').fetchall())"`

## Run tests
`pytest -v`

## Notes
- Guest mode: a random token is stored in an HTTP-only cookie; only its SHA-256 hash is saved. Reports are only readable with that cookie. Clearing cookies makes old reports unreachable (delete them first if you wish).
- The `users` table exists for future accounts; login is not implemented yet.
- Production: set `MAHACAREER_PROD=1`, serve over HTTPS, and update the CORS origins in `backend/main.py`.
- Scoring: see the docstring in `backend/career_engine.py`.
