"""Pydantic schemas that extend fastapi-users base models."""
import uuid

from fastapi_users import schemas as user_schemas


class UserRead(user_schemas.BaseUser[uuid.UUID]):
    full_name: str | None = None


class UserCreate(user_schemas.BaseUserCreate):
    full_name: str | None = None


class UserUpdate(user_schemas.BaseUserUpdate):
    full_name: str | None = None
