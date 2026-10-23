
from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    education: Mapped[str] = mapped_column(String(160), nullable=False)
    skills: Mapped[str] = mapped_column(Text, default="")
    interests: Mapped[str] = mapped_column(Text, default="")
    goals: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )


class LearningProgress(Base):
    __tablename__ = "learning_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    profile_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("student_profiles.id"),
        nullable=False,
        index=True
    )

    career_title: Mapped[str] = mapped_column(String(160), nullable=False)
    item_name: Mapped[str] = mapped_column(String(250), nullable=False)
    item_type: Mapped[str] = mapped_column(String(50), default="skill")
    completed: Mapped[bool] = mapped_column(Boolean, default=False)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
