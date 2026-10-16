from typing import Annotated, Literal, Optional
from pydantic import BaseModel, Field, StringConstraints, field_validator

Short = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=80)]
Tags = Annotated[list[Short], Field(max_length=20)]

class AssessmentIn(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=80)]
    age_range: Literal["Under 15","15-17","18-21","22-25","26-35","36+"]
    education_level: Short
    field_of_study: Short
    favourite_subjects: Tags = []
    interests: Annotated[list[Short], Field(min_length=1, max_length=20)]
    existing_skills: Tags = []
    desired_skills: Tags = []
    work_style: Short
    career_goals: Annotated[str, StringConstraints(strip_whitespace=True, min_length=10, max_length=1000)]
    industries: Tags = []
    experience: Optional[Annotated[str, StringConstraints(strip_whitespace=True, max_length=1000)]] = None

    @field_validator("name", "career_goals", "experience")
    @classmethod
    def no_markup(cls, v):
        if v and ("<" in v or ">" in v):
            raise ValueError("Please remove < and > characters.")
        return v
