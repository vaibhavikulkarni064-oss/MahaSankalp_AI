# KrushiRakshak AI

**Smart Farming. Stronger Farmers. Better Tomorrow.**

A beginner-friendly full-stack prototype for Maharashtra: HTML/CSS/JavaScript, FastAPI, Pydantic and SQLite. Crop suggestions and guidance are transparent sample rules, not a substitute for a local agriculture expert.

## 1. Requirements
- Python 3.10 or newer
- Visual Studio Code
- Internet only for installing Python packages

## 2. Open and run on Windows
Open the `KrushiRakshak_AI` folder in VS Code. Open Terminal → New Terminal and run:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, use Command Prompt terminal and run `.venv\Scripts\activate.bat`, or temporarily use `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in the current PowerShell window.

Set a session secret for development (optional locally; required before deployment):

```powershell
$env:SESSION_SECRET = "replace-this-with-a-long-random-secret"
$env:FRONTEND_ORIGIN = "http://127.0.0.1:5500"
```

Start the backend from the project root:

```powershell
python -m uvicorn backend.main:app --reload --port 8000
```

Visit `http://127.0.0.1:8000/health` and `http://127.0.0.1:8000/docs` to verify the API.

### Launch the frontend
In VS Code, install the **Live Server** extension if needed. Right-click `frontend/index.html` → **Open with Live Server**. The default address `http://127.0.0.1:5500` is configured. Alternatively, from the project root run `python -m http.server 5500 --directory frontend`, then open `http://127.0.0.1:5500`.

Keep the backend and frontend terminals running. Do not open the HTML as a `file://` URL.

## 3. Database and persistence
SQLite database is automatically created at `database/krushirakshak.db`. It is excluded from Git. Reports persist across backend restarts. Each browser session has a signed session cookie; report read/delete routes are scoped to that session. Clearing browser cookies starts a new guest session, so old reports won't be visible from the new session. This is a prototype session model, not a replacement for a production login system.

To initialize manually:

```powershell
python -m database.init_db
```

## 4. Run tests
From project root with the virtual environment activated:

```powershell
pytest -q
```

## 5. Project structure
- `frontend/` — responsive interface and API-connected forms
- `backend/main.py` — FastAPI endpoints and session-scoped report access
- `backend/database.py` — SQLite schema and connection helper
- `backend/crop_engine.py` — configurable, explainable prototype rules
- `backend/schemas.py` — request validation
- `database/init_db.py` — database initialization
- `tests/` — API and rule tests

## Important limitations
- Crop catalogue and rules are sample data. Validate with Maharashtra agriculture experts before real farm decisions.
- The site does not use live weather, soil laboratory results, market rates, or image-based diagnosis.
- Do not use this prototype to choose pesticide products, chemical doses, or a guaranteed irrigation schedule.
- Before deployment, set a strong secret, use HTTPS, add authentication and rate limiting, review CORS, and arrange a privacy/data deletion policy.
