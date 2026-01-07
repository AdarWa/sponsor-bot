from __future__ import annotations

from typing import Sequence
import asyncio

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from .scrape_actions import scrape_action, search_action

from .models import EmailRecord, EmailScrapeTarget, EmailTemplate, SearchScrapeQuery


async def scrape_email_targets(session: AsyncSession) -> str:
    """Collect websites marked for scraping."""

    result = await session.execute(select(EmailScrapeTarget.url))
    websites = result.scalars().all()
    
    emails = await asyncio.to_thread(scrape_action, list(websites))
    
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
    
    urls = await asyncio.to_thread(search_action, list(queries))
    
    for url in urls:
        if not (await session.execute(select(EmailScrapeTarget).where(EmailScrapeTarget.url == url))).scalars().first():
            session.add(EmailScrapeTarget(url=url))
    await session.execute(delete(SearchScrapeQuery))
    await session.commit()
    
    return f"Found {len(urls)} URLs from {len(queries)} search queries"


async def send_email_campaign(session: AsyncSession, template: EmailTemplate, emails: Sequence[str]) -> str:
    """Outline how to send a campaign using the stored template."""

    _ = await session.execute(select(EmailRecord.id).limit(1))
    
    return (
        "Email sending not implemented. Update `scraping.send_email_campaign` to deliver the "
        f"stored template to {len(emails)} recipients."
    )
