from pathlib import Path
import json, os, uuid
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from backend.database import get_db, init_db
from backend.schemas import CropRequest, ProblemRequest, IrrigationRequest
from backend.crop_engine import CATALOGUE, get_recommendations, problem_guidance, irrigation_guidance

app = FastAPI(title='KrushiRakshak AI', version='1.0.0', description='Prototype agricultural guidance for Maharashtra')
frontend_origin = os.getenv('FRONTEND_ORIGIN', 'http://127.0.0.1:5500')
app.add_middleware(CORSMiddleware, allow_origins=[frontend_origin, 'http://localhost:5500'], allow_credentials=True, allow_methods=['GET','POST','DELETE','OPTIONS'], allow_headers=['Content-Type'])
app.add_middleware(SessionMiddleware, secret_key=os.getenv('SESSION_SECRET', 'development-only-change-this-secret-key'), same_site='lax', https_only=False, max_age=60*60*24*30)

@app.on_event('startup')
def startup(): init_db()

def guest_id(request: Request):
    if not request.session.get('guest_id'):
        request.session['guest_id'] = str(uuid.uuid4())
    return request.session['guest_id']

def save_farmer(db, guest, district, name, language):
    row=db.execute('SELECT id FROM farmers WHERE guest_id=? LIMIT 1',(guest,)).fetchone()
    if row:
        db.execute('UPDATE farmers SET district=?, name=COALESCE(?,name), preferred_language=? WHERE id=?',(district,name,language,row['id']))
        return row['id']
    cur=db.execute('INSERT INTO farmers(name,district,preferred_language,guest_id) VALUES(?,?,?,?)',(name,district,language,guest))
    return cur.lastrowid

def report_summary(row):
    return dict(row)

CROP_BASE = 0
PROBLEM_BASE = 1_000_000_000
IRRIGATION_BASE = 2_000_000_000

@app.get('/')
def root(): return {'app':'KrushiRakshak AI','status':'ready','docs':'/docs'}

@app.get('/health')
def health(): return {'status':'healthy','app':'KrushiRakshak AI'}

@app.get('/crops')
def crops(): return {'items': CATALOGUE, 'notice':'Configurable prototype catalogue; verify locally before field use.'}

@app.post('/crop-recommendations')
def crop_recommendations(data: CropRequest, request: Request):
    guest=guest_id(request); result=get_recommendations(data)
    try:
        with get_db() as db:
            farmer=save_farmer(db,guest,data.district,data.name,data.preferred_language)
            cur=db.execute("INSERT INTO crop_assessments(farmer_id,guest_id,district,soil_type,season,irrigation_type,water_availability,land_area,land_unit,crop_preference,constraints) VALUES(?,?,?,?,?,?,?,?,?,?,?)",(farmer,guest,data.district,data.soil_type,data.season,data.irrigation_type,data.water_availability,data.land_area,data.land_unit,data.crop_preference,data.constraints))
            assessment_id=cur.lastrowid
            rec=db.execute('INSERT INTO crop_recommendations(assessment_id,recommended_crops,explanation,limitations) VALUES(?,?,?,?)',(assessment_id,json.dumps(result['candidates']),result['explanation'],result['limitations']))
            report_id=rec.lastrowid
        return {'ok':True,'report_id':report_id,'assessment_id':assessment_id,'type':'crop','result':result}
    except Exception as exc:
        raise HTTPException(status_code=500,detail='Could not save this assessment. Please retry.') from exc

@app.post('/crop-problems')
def crop_problems(data: ProblemRequest, request: Request):
    guest=guest_id(request); result=problem_guidance(data)
    try:
        with get_db() as db:
            cur=db.execute('INSERT INTO crop_problem_reports(guest_id,crop_name,growth_stage,symptoms,duration,possible_causes,guidance) VALUES(?,?,?,?,?,?,?)',(guest,data.crop_name,data.growth_stage,json.dumps(data.symptoms),data.duration,json.dumps(result['possible_causes']),json.dumps(result)))
            rid=cur.lastrowid
        return {'ok':True,'report_id':PROBLEM_BASE + rid,'type':'problem','result':result}
    except Exception as exc: raise HTTPException(status_code=500,detail='Could not save this report. Please retry.') from exc

@app.post('/irrigation-guidance')
def irrigation(data: IrrigationRequest, request: Request):
    guest=guest_id(request); result=irrigation_guidance(data)
    try:
        with get_db() as db:
            cur=db.execute('INSERT INTO irrigation_reports(guest_id,crop_name,soil_type,growth_stage,irrigation_method,rainfall_input,water_availability,guidance) VALUES(?,?,?,?,?,?,?,?)',(guest,data.crop_name,data.soil_type,data.growth_stage,data.irrigation_method,data.rainfall_input,data.water_availability,json.dumps(result)))
            rid=cur.lastrowid
        return {'ok':True,'report_id':IRRIGATION_BASE + rid,'type':'irrigation','result':result}
    except Exception as exc: raise HTTPException(status_code=500,detail='Could not save this report. Please retry.') from exc

@app.get('/reports')
def reports(request: Request):
    guest=guest_id(request); items=[]
    with get_db() as db:
        for r in db.execute("SELECT r.id, a.district AS title, r.created_at, 'crop' AS type FROM crop_recommendations r JOIN crop_assessments a ON a.id=r.assessment_id WHERE a.guest_id=? ORDER BY r.id DESC",(guest,)): items.append(dict(r))
        for r in db.execute("SELECT id + 1000000000 AS id, crop_name AS title, created_at, 'problem' AS type FROM crop_problem_reports WHERE guest_id=? ORDER BY id DESC",(guest,)): items.append(dict(r))
        for r in db.execute("SELECT id + 2000000000 AS id, crop_name AS title, created_at, 'irrigation' AS type FROM irrigation_reports WHERE guest_id=? ORDER BY id DESC",(guest,)): items.append(dict(r))
        items.sort(key=lambda x:x['created_at'], reverse=True)
    return {'items':items,'total':len(items)}

@app.get('/reports/{report_id}')
def get_report(report_id: int, request: Request):
    guest=guest_id(request)
    with get_db() as db:
        if report_id >= IRRIGATION_BASE:
            local_id = report_id - IRRIGATION_BASE
            row=db.execute('SELECT id,crop_name,soil_type,growth_stage,irrigation_method,rainfall_input,water_availability,guidance,created_at FROM irrigation_reports WHERE id=? AND guest_id=?',(local_id,guest)).fetchone()
            if row: return {'id':report_id,'type':'irrigation','data':dict(row)}
        elif report_id >= PROBLEM_BASE:
            local_id = report_id - PROBLEM_BASE
            row=db.execute('SELECT id,crop_name,growth_stage,symptoms,duration,possible_causes,guidance,created_at FROM crop_problem_reports WHERE id=? AND guest_id=?',(local_id,guest)).fetchone()
            if row: return {'id':report_id,'type':'problem','data':dict(row)}
        else:
            row=db.execute('SELECT a.id,a.district,a.soil_type,a.season,a.irrigation_type,a.water_availability,a.land_area,a.land_unit,a.crop_preference,a.constraints,a.created_at,r.recommended_crops,r.explanation,r.limitations FROM crop_recommendations r JOIN crop_assessments a ON a.id=r.assessment_id WHERE r.id=? AND a.guest_id=?',(report_id,guest)).fetchone()
            if row: return {'id':report_id,'type':'crop','data':dict(row)}
    raise HTTPException(status_code=404,detail='Report not found for this session.')

@app.delete('/reports/{report_id}')
def delete_report(report_id: int, request: Request):
    guest=guest_id(request)
    with get_db() as db:
        if report_id >= IRRIGATION_BASE:
            cur=db.execute('DELETE FROM irrigation_reports WHERE id=? AND guest_id=?',(report_id-IRRIGATION_BASE,guest))
        elif report_id >= PROBLEM_BASE:
            cur=db.execute('DELETE FROM crop_problem_reports WHERE id=? AND guest_id=?',(report_id-PROBLEM_BASE,guest))
        else:
            owned=db.execute('SELECT a.id FROM crop_recommendations r JOIN crop_assessments a ON a.id=r.assessment_id WHERE r.id=? AND a.guest_id=?',(report_id,guest)).fetchone()
            if owned:
                cur=db.execute('DELETE FROM crop_assessments WHERE id=? AND guest_id=?',(owned['id'],guest))
            else:
                cur=None
        if cur is None or not cur.rowcount: raise HTTPException(status_code=404,detail='Report not found for this session.')
    return {'ok':True,'deleted':True,'report_id':report_id}

FRONTEND = Path(__file__).resolve().parents[1] / 'frontend'
app.mount('/site', StaticFiles(directory=FRONTEND, html=True), name='site')
