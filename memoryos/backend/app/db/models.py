"""
MemoryOS Backend — SQLAlchemy ORM Models
Phase 1 tables: users, projects, memory_episodes
Schema matches Architecture.md §5.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


class User(Base):
    """
    User account.
    Maps to Architecture.md: users — id, email, name, org_id, preferences
    """

    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    org_id = Column(
        UUID(as_uuid=True), nullable=True, index=True
    )  # Phase 4: multi-org
    preferences = Column(JSONB, default=dict)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    projects = relationship("Project", back_populates="owner", lazy="selectin")

    def __repr__(self) -> str:
        return f"<User {self.email}>"


class Project(Base):
    """
    A project workspace that owns its own memory namespace.
    Maps to Architecture.md: projects — id, owner_id, org_id, name, tech_stack, status
    """

    __tablename__ = "projects"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    org_id = Column(
        UUID(as_uuid=True), nullable=True, index=True
    )  # Phase 4: multi-org
    name = Column(String(255), nullable=False)
    description = Column(Text, default="")
    tech_stack = Column(JSONB, default=list)  # e.g. ["Python", "React", "PostgreSQL"]
    project_type = Column(
        String(50), default="software_dev"
    )  # software_dev | research | business
    status = Column(
        String(50), default="active"
    )  # active | archived | deleted
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    owner = relationship("User", back_populates="projects")
    episodes = relationship(
        "MemoryEpisode", back_populates="project", lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("ix_projects_owner_status", "owner_id", "status"),
    )

    def __repr__(self) -> str:
        return f"<Project {self.name}>"


class MemoryEpisode(Base):
    """
    Episodic memory — Tier 1.
    Stores the full chronological record of every conversation turn.
    Maps to Architecture.md: memory_episodes — role, content, summary,
    embedding_id, confidence

    TTL Policy: Raw turns 30 days → compressed summaries indefinite.
    """

    __tablename__ = "memory_episodes"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    session_id = Column(
        UUID(as_uuid=True), default=uuid.uuid4, nullable=False, index=True
    )
    role = Column(
        String(20), nullable=False
    )  # "user" | "assistant" | "system"
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)  # Phase 3: compressed summary
    embedding_id = Column(
        String(255), nullable=True
    )  # Qdrant point ID for this turn
    confidence = Column(Float, default=1.0)
    token_count = Column(Integer, default=0)

    # Phase 3: Compression fields
    is_compressed = Column(Boolean, default=False)

    # Metadata
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    project = relationship("Project", back_populates="episodes")

    # Indexes — every query MUST be scoped by project_id (Rules.md §2)
    __table_args__ = (
        Index("ix_episodes_project_created", "project_id", "created_at"),
        Index("ix_episodes_project_session", "project_id", "session_id"),
    )

    def __repr__(self) -> str:
        return f"<MemoryEpisode {self.role} @ {self.created_at}>"
