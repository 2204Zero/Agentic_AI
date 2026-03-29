from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, TIMESTAMP
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    submissions = relationship("CodeSubmission", back_populates="user", cascade="all, delete")


class CodeSubmission(Base):
    __tablename__ = "code_submissions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="submissions")
    results = relationship("AnalysisResult", back_populates="submission", cascade="all, delete")

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    submission_id = Column(Integer, ForeignKey("code_submissions.id"))
    submission = relationship("CodeSubmission")

    status = Column(String, default="pending")  # pending, processing, completed, failed
    retry_count = Column(Integer, default=0)

    attempts = Column(Integer, default=0)

    result = Column(JSONB, nullable=True)
    error = Column(String, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, onupdate=func.now())

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)

    submission_id = Column(Integer, ForeignKey("code_submissions.id"))

    analysis = Column(Text)
    issues = Column(Text)
    fixes = Column(Text)
    explanations = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    submission = relationship("CodeSubmission", back_populates="results")


   