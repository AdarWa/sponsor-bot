"""Pydantic schemas that extend fastapi-users base models."""
from datetime import datetime
import uuid

from fastapi_users import schemas as user_schemas
from pydantic import BaseModel, ConfigDict


class UserRead(user_schemas.BaseUser[uuid.UUID]):
    full_name: str | None = None


class UserCreate(user_schemas.BaseUserCreate):
    full_name: str | None = None


class UserUpdate(user_schemas.BaseUserUpdate):
    full_name: str | None = None


class EmailScrapeTargetBase(BaseModel):
    url: str


class EmailScrapeTargetCreate(EmailScrapeTargetBase):
    pass


class EmailScrapeTargetRead(EmailScrapeTargetBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime


class SearchScrapeQueryBase(BaseModel):
    query: str


class SearchScrapeQueryCreate(SearchScrapeQueryBase):
    pass


class SearchScrapeQueryRead(SearchScrapeQueryBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime


class EmailRecordBase(BaseModel):
    email: str


class EmailRecordCreate(EmailRecordBase):
    pass


class EmailRecordRead(EmailRecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime


class EmailTemplateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    subject: str
    body: str


class EmailTemplateUpdate(BaseModel):
    subject: str
    body: str
