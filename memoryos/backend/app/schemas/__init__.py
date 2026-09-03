"""
MemoryOS Backend — Pydantic Schemas
Request/response models for all Phase 1 API endpoints.
Standard error shape enforced per Rules.md §3.
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ===========================
# Error Response (Rules.md §3)
# ===========================

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = {}


class ErrorResponse(BaseModel):
    error: ErrorDetail


# ===========================
# Auth Schemas
# ===========================

class UserRegister(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    """Partial update for user profile."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None


class ChangePassword(BaseModel):
    """Change password request."""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)


# ===========================
# Project Schemas
# ===========================

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(default="", max_length=2000)
    tech_stack: list[str] = Field(default_factory=list)
    project_type: str = Field(
        default="software_dev",
        pattern="^(software_dev|research|business)$",
    )


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    tech_stack: Optional[list[str]] = None
    project_type: Optional[str] = Field(
        None, pattern="^(software_dev|research|business)$"
    )
    status: Optional[str] = Field(
        None, pattern="^(active|archived)$"
    )


class ProjectResponse(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    description: str
    tech_stack: list[str]
    project_type: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectListResponse(BaseModel):
    projects: list[ProjectResponse]
    total: int


# ===========================
# Chat Schemas
# ===========================

class ChatMessage(BaseModel):
    """User's chat message to a project."""
    message: str = Field(..., min_length=1, max_length=32000)
    session_id: Optional[UUID] = None  # Optional: continue existing session


class ChatResponse(BaseModel):
    """Full chat response (non-streaming fallback)."""
    response: str
    session_id: UUID
    sources_used: int = 0  # How many memory chunks were retrieved


# ===========================
# Memory Schemas
# ===========================

class EpisodeResponse(BaseModel):
    id: UUID
    session_id: UUID
    role: str
    content: str
    confidence: float
    token_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class EpisodeListResponse(BaseModel):
    episodes: list[EpisodeResponse]
    total: int


class SessionListResponse(BaseModel):
    """List of unique sessions for a project."""
    sessions: list[dict[str, Any]]  # [{session_id, first_message, created_at, turn_count}]
    total: int


# ===========================
# Health Schemas
# ===========================

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
    phase: int = 1
    services: dict[str, str] = {}  # service_name → "connected" | "error"
