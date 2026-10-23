
from pydantic import BaseModel, Field, ConfigDict


class ProfileCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    education: str = Field(min_length=1, max_length=160)
    skills: list[str] = []
    interests: str = ""
    goals: str = ""


class ProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    education: str
    skills: str
    interests: str
    goals: str


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)


class LearningProgressUpdate(BaseModel):
    career_title: str = Field(min_length=1, max_length=160)
    item_name: str = Field(min_length=1, max_length=250)
    item_type: str = Field(default="skill", max_length=50)
    completed: bool = False


class LearningProgressOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    profile_id: int
    career_title: str
    item_name: str
    item_type: str
    completed: bool
