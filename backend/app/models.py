"""Database models used across the application."""
import uuid

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    """Primary user table managed by fastapi-users."""

    full_name: Mapped[str | None] = mapped_column(String(length=255), nullable=True)
