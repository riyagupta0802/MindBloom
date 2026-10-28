"""
==============================================================================
MINDBLOOM BACKEND — PYDANTIC SCHEMAS (PHASE 3)
Project: MindBloom — AI-Powered Cognitive & Memory Assistance Platform
Technology: Python 3, Pydantic v2
==============================================================================
"""

import re
from datetime import datetime
from typing import Optional, Dict, Literal, List
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict


# Allowed types and difficulty tiers
UserType = Literal["elderly", "caregiver"]
DifficultyLevel = Literal["easy", "medium", "hard"]


# -----------------------------------------------------------------------------
# User Schemas
# -----------------------------------------------------------------------------
class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Full display name of user")
    email: str = Field(..., min_length=5, max_length=150, description="Valid unique email address")
    user_type: UserType = Field(default="elderly", description="User role: 'elderly' or 'caregiver'")

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, value: str) -> str:
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(pattern, value.strip()):
            raise ValueError("Invalid email format. Please provide a valid email (e.g. user@example.com).")
        return value.strip().lower()

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        clean = value.strip()
        if not clean:
            raise ValueError("Name cannot be empty or whitespace only.")
        return clean


class UserCreate(UserBase):
    """Schema for registering a new user / demo profile."""
    pass


class UserResponse(UserBase):
    """Schema returned when reading user profiles."""
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserRegisterRequest(BaseModel):
    """Schema for new user registration."""
    name: str = Field(..., min_length=2, max_length=100, description="Full display name of the user")
    email: str = Field(..., min_length=5, max_length=150, description="Valid email address")
    user_type: UserType = Field(default="elderly", description="Role: 'elderly' or 'caregiver'")
    password: str = Field(..., min_length=6, max_length=100, description="Password (at least 6 characters)")
    confirm_password: str = Field(..., min_length=6, max_length=100, description="Password confirmation")

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, value: str) -> str:
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(pattern, value.strip()):
            raise ValueError("Invalid email format. Please provide a valid email (e.g. user@example.com).")
        return value.strip().lower()

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        clean = value.strip()
        if not clean or len(clean) < 2:
            raise ValueError("Name must be at least 2 characters.")
        return clean

    @model_validator(mode="after")
    def validate_password_match(self) -> "UserRegisterRequest":
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match. Please re-enter your password.")
        return self


class UserLoginRequest(BaseModel):
    """Schema for user authentication / login."""
    email: str = Field(..., min_length=3, max_length=150, description="Registered email address")
    password: str = Field(..., min_length=1, max_length=100, description="User password")

    @field_validator("email")
    @classmethod
    def clean_email(cls, value: str) -> str:
        return value.strip().lower()


class AuthResponse(BaseModel):
    """Response returned upon successful authentication (login or register)."""
    status: str = "success"
    message: str
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# -----------------------------------------------------------------------------
# Game Session Schemas
# -----------------------------------------------------------------------------
class GameSessionCreate(BaseModel):
    """
    Schema for saving a completed gameplay session.
    Matches the data structure produced by the Phase 2 Memory Matching game.
    """
    user_id: int = Field(..., gt=0, description="ID of the user who completed the game")
    game_name: str = Field(default="Memory Match", min_length=1, max_length=50, description="Name of cognitive game")
    difficulty: DifficultyLevel = Field(..., description="Difficulty played: 'easy', 'medium', or 'hard'")
    score: int = Field(..., ge=0, description="Final score, non-negative")
    accuracy: float = Field(..., ge=0.0, le=100.0, description="Accuracy percentage (0.0 to 100.0)")
    response_time: int = Field(..., ge=0, description="Time taken to finish the game in seconds")
    total_attempts: int = Field(..., ge=0, description="Total pair-revealing attempts")
    mistakes: int = Field(..., ge=0, description="Total mismatched pair attempts")
    hints_used: int = Field(default=0, ge=0, description="Number of hints requested")
    matched_pairs: int = Field(..., ge=0, description="Number of pairs matched")
    total_pairs: int = Field(..., gt=0, description="Total pairs required for the game")
    recommended_difficulty: Optional[str] = Field(default=None, description="AI recommended next difficulty: 'Easy', 'Medium', or 'Hard'")
    started_at: Optional[datetime] = Field(default=None, description="Game start timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="Game completion timestamp")
    client_session_id: Optional[str] = Field(default=None, max_length=64, description="Unique client session ID for deduplication")

    @model_validator(mode="after")
    def validate_matched_lte_total(self) -> "GameSessionCreate":
        if self.matched_pairs > self.total_pairs:
            raise ValueError(f"Matched pairs ({self.matched_pairs}) cannot exceed total pairs ({self.total_pairs}).")
        return self


class GameSessionResponse(GameSessionCreate):
    """Full database representation of a recorded game session."""
    session_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GameSessionCreateResponse(BaseModel):
    """Response returned upon successfully storing a game session."""
    status: str = "success"
    session_id: int
    message: str = "Game session recorded successfully."
    is_duplicate: bool = False


# -----------------------------------------------------------------------------
# Performance & Statistics Schemas
# -----------------------------------------------------------------------------
class DifficultyBreakdown(BaseModel):
    easy: int = 0
    medium: int = 0
    hard: int = 0


class UserPerformanceResponse(BaseModel):
    """Aggregate statistics for a user's gameplay history."""
    user_id: int
    total_games: int
    average_score: float
    average_accuracy: float
    average_response_time: float
    total_mistakes: int
    total_hints_used: int
    games_by_difficulty: DifficultyBreakdown

    model_config = ConfigDict(from_attributes=True)


class ProgressSessionPoint(BaseModel):
    session_id: int
    session_number: int
    date: str
    difficulty: str
    score: int
    accuracy: float
    response_time: int
    mistakes: int
    hints_used: int
    recommended_difficulty: Optional[str] = None


class AnalyticsProgressResponse(BaseModel):
    """Chronological progress data formatted for charts and trend tracking."""
    user_id: int
    total_sessions: int
    sessions: List[ProgressSessionPoint]
    labels: List[str]
    score_trend: List[int]
    accuracy_trend: List[float]
    response_time_trend: List[int]
    difficulty_distribution: DifficultyBreakdown

    model_config = ConfigDict(from_attributes=True)


# -----------------------------------------------------------------------------
# ML Adaptive Difficulty Schemas (Phase 4)
# -----------------------------------------------------------------------------
class MLPredictionRequest(BaseModel):
    """
    Schema for requesting next-session difficulty recommendation.
    Validates all gameplay metrics to reject invalid/negative values.
    """
    accuracy: float = Field(..., ge=0.0, le=100.0, description="Player accuracy percentage (0 to 100)")
    response_time: int = Field(..., ge=0, description="Elapsed game response time in seconds")
    mistakes: int = Field(..., ge=0, description="Count of incorrect matching attempts")
    score: int = Field(..., ge=0, description="Game score achieved")
    hints_used: int = Field(default=0, ge=0, description="Number of hints used")
    previous_difficulty: Literal["easy", "medium", "hard", "Easy", "Medium", "Hard"] = Field(
        ..., description="Difficulty tier of the completed game"
    )


class MLPredictionResponse(BaseModel):
    """
    Recommended difficulty and prediction probabilities from Random Forest model.
    """
    recommended_difficulty: Literal["Easy", "Medium", "Hard"]
    probabilities: Dict[str, float]
    confidence: float
    model_version: str = "1.0.0"
    disclaimer: str = (
        "Academic prototype for cognitive gaming difficulty adaptation only. "
        "Strictly not a medical diagnosis or clinical assessment."
    )


