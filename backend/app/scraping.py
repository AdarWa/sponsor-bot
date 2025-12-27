from __future__ import annotations

from typing import Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api import ScrapeApi

from .models import EmailRecord, EmailScrapeTarget, EmailTemplate, SearchScrapeQuery


async def scrape_email_targets(session: AsyncSession) -> str:
    """Collect websites marked for scraping."""

    result = await session.execute(select(EmailScrapeTarget.url))
    websites = result.scalars().all()
    
    emails = await ScrapeApi().scrape_website(list(websites))
    
    for email in emails:
        if not (await session.execute(select(EmailRecord).where(EmailRecord.email == email))).scalars().first():
            session.add(EmailRecord(email=email))
    await session.execute(delete(EmailScrapeTarget))
    await session.commit()
    
    return f"Found {len(emails)} email addresses from {len(websites)} websites"


async def scrape_search_queries(session: AsyncSession) -> str:
    """Collect Google search queries."""

    result = await session.execute(select(SearchScrapeQuery.query))
    queries = result.scalars().all()
    return (
        "Search scraping not implemented. Update `scraping.scrape_search_queries` to run the "
        f"{len(queries)} queries against Google (or another source) and insert new websites into "
        "`EmailScrapeTarget`."
    )


async def send_email_campaign(session: AsyncSession, template: EmailTemplate, emails: Sequence[str]) -> str:
    """Outline how to send a campaign using the stored template."""

    _ = await session.execute(select(EmailRecord.id).limit(1))
    
    return (
        "Email sending not implemented. Update `scraping.send_email_campaign` to deliver the "
        f"stored template to {len(emails)} recipients."
    )
