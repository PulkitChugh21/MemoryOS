"""
MemoryOS Backend — SQLAlchemy ORM Models
Phase 1 tables: users, projects, memory_episodes
Phase 2 tables: memory_facts, project_files
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
    facts = relationship(
        "MemoryFact", back_populates="project", lazy="selectin"
    )
    files = relationship(
        "ProjectFile", back_populates="project", lazy="selectin"
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


class MemoryFact(Base):
    """
    Structured memory — Tier 3 (Phase 2).
    Hard facts and preferences as key-value records.
    Exact-match queryable. Never expires unless explicitly updated.
    Maps to Architecture.md §3 Tier 3, §5: memory_facts.
    """

    __tablename__ = "memory_facts"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    fact_type = Column(
        String(50), nullable=False
    )  # decision | preference | entity | tech_stack | goal | milestone | open_question | file_fact
    key = Column(String(500), nullable=False)
    value = Column(Text, nullable=False)
    source = Column(
        String(50), nullable=False, default="conversation"
    )  # conversation | file_upload | user_explicit
    source_episode_id = Column(
        UUID(as_uuid=True),
        ForeignKey("memory_episodes.id", ondelete="SET NULL"),
        nullable=True,
    )
    confidence = Column(Float, default=0.8)

    # Phase 3: Self-healing fields
    is_stale = Column(Boolean, default=False)
    ttl_days = Column(Integer, nullable=True)  # Domain-aware: code 7d, decisions 30d, goals 90d

    # Metadata
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
    project = relationship("Project", back_populates="facts")
    source_episode = relationship("MemoryEpisode", foreign_keys=[source_episode_id])

    # Indexes — every query scoped by project_id (Rules.md §2)
    __table_args__ = (
        Index("ix_facts_project_type", "project_id", "fact_type"),
        Index("ix_facts_project_key", "project_id", "key"),
        Index("ix_facts_project_stale", "project_id", "is_stale"),
    )

    def __repr__(self) -> str:
        return f"<MemoryFact [{self.fact_type}] {self.key}>"


class ProjectFile(Base):
    """
    File metadata and versioning (Phase 2).
    Tracks uploaded files stored in Supabase Storage.
    Each re-upload creates a new version; old versions are kept with is_current=False.
    Maps to Architecture.md §2.2 File Upload Flow.
    """

    __tablename__ = "project_files"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)  # Supabase Storage path
    mime_type = Column(String(100), nullable=False, default="text/plain")
    size_bytes = Column(Integer, nullable=False, default=0)
    version = Column(Integer, nullable=False, default=1)
    parent_version_id = Column(
        UUID(as_uuid=True),
        ForeignKey("project_files.id", ondelete="SET NULL"),
        nullable=True,
    )
    diff_summary = Column(Text, nullable=True)  # LLM-generated diff vs previous version
    chunk_count = Column(Integer, nullable=False, default=0)
    is_current = Column(Boolean, nullable=False, default=True)

    # Metadata
    uploaded_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    project = relationship("Project", back_populates="files")
    parent_version = relationship("ProjectFile", remote_side="ProjectFile.id")

    # Indexes — every query scoped by project_id (Rules.md §2)
    __table_args__ = (
        Index("ix_files_project_filename", "project_id", "filename", "is_current"),
        Index("ix_files_project_current", "project_id", "is_current"),
    )
