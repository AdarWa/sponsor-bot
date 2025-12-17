"""Database models used across the application."""
from datetime import datetime, timezone
import uuid

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    """Primary user table managed by fastapi-users."""

    full_name: Mapped[str | None] = mapped_column(String(length=255), nullable=True)


class EmailScrapeTarget(Base):
    """Website to scan for potential contacts."""

    __tablename__ = "email_scrape_targets"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    url: Mapped[str] = mapped_column(String(length=512), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class SearchScrapeQuery(Base):
    """Google search query definitions for scraping."""

    __tablename__ = "search_scrape_queries"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    query: Mapped[str] = mapped_column(String(length=255), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class EmailRecord(Base):
    """Individual email addresses collected from scraping."""

    __tablename__ = "email_records"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(length=320), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class EmailTemplate(Base):
    """Stores the outreach template used when sending campaigns."""

    __tablename__ = "email_templates"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    subject: Mapped[str] = mapped_column(String(length=255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
