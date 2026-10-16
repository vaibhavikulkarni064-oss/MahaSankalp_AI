from pydantic import BaseModel, Field, ConfigDict
from typing import Literal

class CropRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    district: str = Field(min_length=2, max_length=80)
    soil_type: Literal['Black soil','Alluvial soil','Red soil','Laterite soil','Sandy soil','Mixed/unknown']
    season: Literal['Kharif','Rabi','Summer','Year-round / protected']
    irrigation_type: Literal['Rainfed','Canal','Well / borewell','Drip','Sprinkler','Other / mixed']
    water_availability: Literal['Low','Moderate','High']
    land_area: float = Field(gt=0, le=100000)
    land_unit: Literal['acre','hectare'] = 'acre'
    crop_preference: str | None = Field(default=None, max_length=80)
    constraints: str | None = Field(default=None, max_length=500)
    name: str | None = Field(default=None, max_length=100)
    preferred_language: Literal['en','mr'] = 'en'

class ProblemRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    crop_name: str = Field(min_length=2, max_length=80)
    growth_stage: Literal['Seedling','Vegetative','Flowering','Fruiting / grain filling','Maturity','Unknown']
    symptoms: list[str] = Field(min_length=1, max_length=8)
    duration: Literal['1–2 days','3–7 days','More than a week','Not sure']

class IrrigationRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    crop_name: str = Field(min_length=2, max_length=80)
    soil_type: Literal['Black soil','Alluvial soil','Red soil','Laterite soil','Sandy soil','Mixed/unknown']
    growth_stage: Literal['Seedling','Vegetative','Flowering','Fruiting / grain filling','Maturity','Unknown']
    irrigation_method: Literal['Flood / furrow','Drip','Sprinkler','Rainfed','Other']
    rainfall_input: str = Field(min_length=1, max_length=100)
    water_availability: Literal['Low','Moderate','High']
