
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from backend.database import Base, engine, get_db
from backend.models import StudentProfile, LearningProgress
from backend.schemas import (
    ProfileCreate,
    ProfileOut,
    ChatRequest,
    LearningProgressUpdate,
    LearningProgressOut,
)
from ml.recommender import recommend_careers, career_chat, CAREERS

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Career Recommendation Agent API",
    version="1.0.0",
    description="Career recommendations, skill-gap analysis, learning roadmap and career guidance."
)


@app.get("/")
def root():
    return {
        "message": "Career Recommendation Agent API is running",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/profiles", response_model=ProfileOut, status_code=201)
def create_profile(payload: ProfileCreate, db: Session = Depends(get_db)):
    profile = StudentProfile(
        name=payload.name.strip(),
        education=payload.education.strip(),
        skills=", ".join(s.strip() for s in payload.skills if s.strip()),
        interests=payload.interests.strip(),
        goals=payload.goals.strip()
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@app.get("/profiles/{profile_id}", response_model=ProfileOut)
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    profile = db.get(StudentProfile, profile_id)

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile


@app.post("/recommendations")
def recommendations(payload: ProfileCreate):
    return {
        "recommendations": recommend_careers(
            payload.skills,
            payload.interests,
            payload.goals
        )
    }


@app.post("/chat")
def chat(payload: ChatRequest):
    return {"answer": career_chat(payload.question)}


@app.get("/careers")
def careers():
    return {"careers": CAREERS}


# Save or update one learning-progress item
@app.put(
    "/profiles/{profile_id}/learning-progress",
    response_model=LearningProgressOut
)
def save_learning_progress(
    profile_id: int,
    payload: LearningProgressUpdate,
    db: Session = Depends(get_db)
):
    profile = db.get(StudentProfile, profile_id)

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    progress = (
        db.query(LearningProgress)
        .filter(
            LearningProgress.profile_id == profile_id,
            LearningProgress.career_title == payload.career_title,
            LearningProgress.item_name == payload.item_name,
            LearningProgress.item_type == payload.item_type
        )
        .first()
    )

    if progress:
        progress.completed = payload.completed
    else:
        progress = LearningProgress(
            profile_id=profile_id,
            career_title=payload.career_title,
            item_name=payload.item_name,
            item_type=payload.item_type,
            completed=payload.completed
        )
        db.add(progress)

    db.commit()
    db.refresh(progress)
    return progress


# Retrieve all saved learning-progress items for one profile
@app.get(
    "/profiles/{profile_id}/learning-progress",
    response_model=list[LearningProgressOut]
)
def get_learning_progress(
    profile_id: int,
    db: Session = Depends(get_db)
):
    profile = db.get(StudentProfile, profile_id)

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return (
        db.query(LearningProgress)
        .filter(LearningProgress.profile_id == profile_id)
        .order_by(LearningProgress.id)
        .all()
    )
