from backend.schemas import CropRequest, ProblemRequest, IrrigationRequest
from backend.crop_engine import get_recommendations, problem_guidance, irrigation_guidance

def test_crop_rules_return_explanation():
    data=CropRequest(district='Solapur',soil_type='Black soil',season='Rabi',irrigation_type='Well / borewell',water_availability='Low',land_area=2,land_unit='acre')
    result=get_recommendations(data)
    assert result['candidates']
    assert result['explanation']
    assert result['limitations']

def test_problem_guidance_is_not_diagnosis():
    data=ProblemRequest(crop_name='Soybean',growth_stage='Vegetative',symptoms=['Yellowing leaves'],duration='3–7 days')
    result=problem_guidance(data)
    assert result['possible_causes']
    assert 'not a diagnosis' in result['notice']

def test_irrigation_has_limitations():
    data=IrrigationRequest(crop_name='Cotton',soil_type='Black soil',growth_stage='Flowering',irrigation_method='Drip',rainfall_input='No recent rain',water_availability='Low')
    result=irrigation_guidance(data)
    assert result['guidance']
    assert 'No exact irrigation volume' in result['notice']
