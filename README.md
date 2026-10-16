# MahaSankalp AI — Unified Five-Sector Portal

This folder combines the five supplied sector projects under one professional homepage. The original sector source folders are retained, while Python virtual environments and cache files were intentionally excluded from the combined copy. Your original ZIP files are unchanged.

## Included sectors

1. **KrushiRakshak AI** — agriculture guidance
2. **MahaSuraksha AI** — cyber safety and fraud risk assessment
3. **JeevanSetu AI** — healthcare emergency priority guidance
4. **MahaJalNet** — water management and flood risk prediction
5. **MahaCareer AI** — career profile assessment

## Run on Windows (recommended)

1. Extract the `MahaSankalp_AI.zip` file to any location you choose, for example `D:\Projects\MahaSankalp_AI`.
2. Install Python 3.10+ and make sure the `py` command works in Command Prompt.
3. Open the extracted `MahaSankalp_AI` folder in VS Code.
4. Run `setup_all.bat` once to create an individual `.venv` and install each sector's dependencies.
5. After setup completes, double-click `start_all.bat`.
6. Open `http://127.0.0.1:5500/` if it does not open automatically.
7. Keep all opened terminal windows running while using the applications.

The main portal is served from port 5500. API services use ports 8000–8004. MahaCareer AI serves its own frontend from port 8004 because its existing frontend and report APIs are hosted together. MahaJalNet's frontend prediction requests are configured to use port 8003.

## API health checks

- KrushiRakshak AI: `http://127.0.0.1:8000/health`
- MahaSuraksha AI: `http://127.0.0.1:8001/`
- JeevanSetu AI: `http://127.0.0.1:8002/`
- MahaJalNet: `http://127.0.0.1:8003/`
- MahaCareer AI: `http://127.0.0.1:8004/health`

Interactive API docs (where enabled) are available at `/docs` on each backend port.

## Notes and honest limitations

- Sector-specific data models, forms and backend logic are retained from the supplied folders; this integration does not certify every feature as production-ready.
- The original JeevanSetu and MahaSuraksha code currently returns analysis results but does not show persistent case storage in the supplied backend code. Treat these as prototypes until storage and access control are implemented and tested.
- Do not rely on prototype outputs as a substitute for official emergency services, medical advice, police reporting channels, or qualified agricultural advice.
- `MahaJalNet` may rely on online map/weather services in some screens. Those features require an internet connection.
- Local development services are intended for your laptop only. Do not expose them publicly without security review, authentication, HTTPS and deployment configuration.

## Change folder destination

You can move or extract this entire folder to another drive or directory. Run `setup_all.bat` and `start_all.bat` from the new location. Do not move only one sector folder out of the combined root because the portal links expect the five sector folders to stay together.
