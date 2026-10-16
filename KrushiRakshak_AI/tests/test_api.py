from fastapi.testclient import TestClient
from backend import database
from backend.main import app

def test_health_and_crop_submission(tmp_path, monkeypatch):
    monkeypatch.setattr(database, 'DB_PATH', tmp_path / 'test.db')
    with TestClient(app) as client:
        assert client.get('/health').status_code == 200
        payload={'district':'Solapur','soil_type':'Black soil','season':'Rabi','irrigation_type':'Well / borewell','water_availability':'Low','land_area':2,'land_unit':'acre','preferred_language':'en'}
        response=client.post('/crop-recommendations',json=payload)
        assert response.status_code == 200
        report_id=response.json()['report_id']
        assert response.json()['ok'] is True
        reports=client.get('/reports').json()
        assert reports['total'] == 1
        assert reports['items'][0]['id'] == report_id
        assert client.get(f'/reports/{report_id}').status_code == 200
        assert client.delete(f'/reports/{report_id}').status_code == 200
        assert client.get(f'/reports/{report_id}').status_code == 404

def test_invalid_crop_submission_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(database, 'DB_PATH', tmp_path / 'test-invalid.db')
    with TestClient(app) as client:
        response=client.post('/crop-recommendations',json={'district':'','land_area':-1})
        assert response.status_code == 422

def test_problem_and_irrigation_reports_are_unique_and_deletable(tmp_path, monkeypatch):
    monkeypatch.setattr(database, 'DB_PATH', tmp_path / 'test-mixed.db')
    with TestClient(app) as client:
        problem=client.post('/crop-problems',json={'crop_name':'Soybean','growth_stage':'Vegetative','symptoms':['Yellowing leaves'],'duration':'3–7 days'}).json()
        irrigation=client.post('/irrigation-guidance',json={'crop_name':'Cotton','soil_type':'Black soil','growth_stage':'Flowering','irrigation_method':'Drip','rainfall_input':'No recent rain','water_availability':'Low'}).json()
        assert problem['report_id'] != irrigation['report_id']
        assert client.get('/reports').json()['total'] == 2
        assert client.get(f"/reports/{problem['report_id']}").json()['type'] == 'problem'
        assert client.get(f"/reports/{irrigation['report_id']}").json()['type'] == 'irrigation'
        assert client.delete(f"/reports/{problem['report_id']}").status_code == 200
        assert client.delete(f"/reports/{irrigation['report_id']}").status_code == 200
