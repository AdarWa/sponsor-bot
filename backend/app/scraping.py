"""Utility helpers that describe how to plug in real scraping/email logic."""

from __future__ import annotations

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import EmailRecord, EmailScrapeTarget, EmailTemplate, SearchScrapeQuery


async def scrape_email_targets(session: AsyncSession) -> str:
    """Collect websites marked for scraping."""

    result = await session.execute(select(EmailScrapeTarget.url))
    websites = result.scalars().all()
    return (
        "Email scraping not implemented. Update `scraping.scrape_email_targets` to crawl the "
        f"{len(websites)} tracked websites and persist discovered emails."
    )


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
    """Outline how to send a campaign using the stored template.

    Suggested implementation steps:

    1. Choose an email provider/SDK (SendGrid, AWS SES, SMTP, etc.).
    2. Iterate over ``emails`` and send each message using ``template.subject``/``template.body``.
       Consider queuing or batching to respect provider rate limits.
    3. Log delivery results to a new table if you need auditing.
    """

    _ = await session.execute(select(EmailRecord.id).limit(1))
    return (
        "Email sending not implemented. Update `scraping.send_email_campaign` to deliver the "
        f"stored template to {len(emails)} recipients."
    )
