"""Dashboard endpoints for verified users."""
from __future__ import annotations
from uuid import UUID

from datetime import datetime, timezone
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import fastapi_users
from .database import get_async_session
from .models import EmailRecord, EmailScrapeTarget, EmailTemplate, SearchScrapeQuery, User
from .schemas import (
    EmailRecordCreate,
    EmailRecordRead,
    EmailScrapeTargetCreate,
    EmailScrapeTargetRead,
    EmailTemplateRead,
    EmailTemplateUpdate,
    SearchScrapeQueryCreate,
    SearchScrapeQueryRead,
)
from .scraping import scrape_email_targets, scrape_search_queries, send_email_campaign

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

current_verified_user = fastapi_users.current_user(active=True, verified=True)


def _normalize_url(url: str) -> str:
    cleaned = url.strip()
    if cleaned.endswith("/"):
        cleaned = cleaned.rstrip("/")
    return cleaned.lower()


def _normalize_email(email: str) -> str:
    return email.strip().lower()


async def _ensure_template(session: AsyncSession) -> EmailTemplate:
    result = await session.execute(select(EmailTemplate))
    template = result.scalars().first()
    if template:
        return template
    template = EmailTemplate(
        subject="Sponsorship Opportunity",
        body="Hi there,\n\nWe would love to partner with you. Let us know if you're interested!\n",
    )
    session.add(template)
    await session.commit()
    await session.refresh(template)
    return template


@router.get("/websites", response_model=list[EmailScrapeTargetRead])
async def list_websites(
    session: AsyncSession = Depends(get_async_session),
    _: User = Depends(current_verified_user),
) -> list[EmailScrapeTarget]:
    result = await session.execute(select(EmailScrapeTarget).order_by(EmailScrapeTarget.created_at.desc()))
    return list(result.scalars().all())


@router.post("/websites", response_model=EmailScrapeTargetRead, status_code=status.HTTP_201_CREATED)
async def add_website(
    payload: EmailScrapeTargetCreate,
    session: AsyncSession = Depends(get_async_session),
    _: User = Depends(current_verified_user),
) -> EmailScrapeTarget:
    normalized = _normalize_url(payload.url)
    existing = await session.execute(select(EmailScrapeTarget).where(EmailScrapeTarget.url == normalized))
    if existing.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Website already tracked.")

    target = EmailScrapeTarget(url=normalized)
    session.add(target)
    try:
        await session.commit()
    except IntegrityError as exc:  # pragma: no cover - informative error
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Website already exists.") from exc
    await session.refresh(target)
    return target


@router.delete("/websites/{target_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_website(
    target_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    _: User = Depends(current_verified_user),
) -> None:
    target = await session.get(EmailScrapeTarget, target_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Website not found")
    await session.delete(target)
    await session.commit()


@router.post("/websites/scrape")
async def trigger_email_scrape(
    session: AsyncSession = Depends(get_async_session),
    _: User = Depends(current_verified_user),
) -> dict[str, str]:
    message = await scrape_email_targets(session)
    return {"status": "pending", "message": message}


@router.get("/queries", response_model=list[SearchScrapeQueryRead])
async def list_queries(
    session: AsyncSession = Depends(get_async_session),
    _: User = Depends(current_verified_user),
) -> list[SearchScrapeQuery]:
    result = await session.execute(select(SearchScrapeQuery).order_by(SearchScrapeQuery.created_at.desc()))
    return list(result.scalars().all())


@router.post("/queries", response_model=SearchScrapeQueryRead, status_code=status.HTTP_201_CREATED)
async def add_query(
    payload: SearchScrapeQueryCreate,
    session: AsyncSession = Depends(get_async_session),
    _: User = Depends(current_verified_user),
) -> SearchScrapeQuery:
    query = SearchScrapeQuery(query=payload.query.strip())
    session.add(query)
    try:
        await session.commit()
    except IntegrityError as exc:  # pragma: no cover - informative error
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Query already exists.") from exc
    await session.refresh(query)
    return query


@router.delete("/queries/{query_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_query(
    query_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    _: User = Depends(current_verified_user),
) -> None:
    query = await session.get(SearchScrapeQuery, query_id)
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Query not found")
    await session.delete(query)
    await session.commit()


@router.post("/queries/scrape")
async def trigger_search_scrape(
    session: AsyncSession = Depends(get_async_session),
    _: User = Depends(current_verified_user),
) -> dict[str, str]:
    message = await scrape_search_queries(session)
    return {"status": "pending", "message": message}


@router.get("/email-template", response_model=EmailTemplateRead)
async def get_email_template(
    session: AsyncSession = Depends(get_async_session),
    _: User = Depends(current_verified_user),
) -> EmailTemplate:
    template = await _ensure_template(session)
    return template


@router.put("/email-template", response_model=EmailTemplateRead)
async def update_email_template(
    payload: EmailTemplateUpdate,
    session: AsyncSession = Depends(get_async_session),
    _: User = Depends(current_verified_user),
) -> EmailTemplate:
    template = await _ensure_template(session)
    template.subject = payload.subject
    template.body = payload.body
    session.add(template)
    await session.commit()
    await session.refresh(template)
    return template


@router.post("/email/send")
async def trigger_email_send(
    session: AsyncSession = Depends(get_async_session),
    _: User = Depends(current_verified_user),
) -> dict[str, str]:
    template = await _ensure_template(session)
    result = await session.execute(select(EmailRecord))
    records = list(result.scalars().all())
    emails = [record.email for record in records]
    message = await send_email_campaign(session, template, emails)

    if records:
        timestamp = datetime.now(timezone.utc)
        for record in records:
            record.last_sent_at = timestamp
            record.send_count = (record.send_count or 0) + 1
            session.add(record)
        await session.commit()

    return {"status": "pending", "message": message}
@router.get("/emails", response_model=list[EmailRecordRead])
async def list_emails(
    session: AsyncSession = Depends(get_async_session),
    _: User = Depends(current_verified_user),
) -> list[EmailRecord]:
    result = await session.execute(select(EmailRecord).order_by(EmailRecord.created_at.desc()))
    return list(result.scalars().all())


@router.post("/emails", response_model=EmailRecordRead, status_code=status.HTTP_201_CREATED)
async def add_email(
    payload: EmailRecordCreate,
    session: AsyncSession = Depends(get_async_session),
    _: User = Depends(current_verified_user),
) -> EmailRecord:
    normalized = _normalize_email(payload.email)
    existing = await session.execute(select(EmailRecord).where(EmailRecord.email == normalized))
    if existing.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already tracked.")

    record = EmailRecord(email=normalized)
    session.add(record)
    try:
        await session.commit()
    except IntegrityError as exc:  # pragma: no cover
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists.") from exc
    await session.refresh(record)
    return record


@router.delete("/emails/{email_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_email(
    email_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    _: User = Depends(current_verified_user),
) -> None:
    record = await session.get(EmailRecord, email_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")
    await session.delete(record)
    await session.commit()
