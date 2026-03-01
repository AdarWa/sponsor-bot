"""Pydantic schemas for API payloads."""
from datetime import datetime
import uuid

from pydantic import BaseModel, ConfigDict


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
    last_sent_at: datetime | None = None
    send_count: int


class EmailTemplateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    subject: str
    body: str


class EmailTemplateUpdate(BaseModel):
    subject: str
    body: str
