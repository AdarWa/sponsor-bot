from __future__ import annotations

from typing import Iterable

from ddgs import DDGS
from extract_emails import DefaultWorker
from extract_emails.browsers import HttpxBrowser
from extract_emails.link_filters import ContactInfoLinkFilter
from fastapi import APIRouter
from pydantic import BaseModel

from .scrape_email_extractor import AdvancedEmailExtractor
from .scrape_targets import CONTACT_PATHS

router = APIRouter(prefix="/api", tags=["scrape-actions"])


class SearchPayload(BaseModel):
    queries: list[str]


class ScrapePayload(BaseModel):
    urls: list[str]


def search_action(queries: Iterable[str]) -> list[str]:
    urls: list[str] = []

    for query in queries:
        result = DDGS().text(
            query,
            region="il-he",
            safesearch="off",
            timelimit="y",
            page=1,
            backend="auto",
        )
        urls += [item["href"] for item in result]

    return list(set(url.split("/")[0] + "//" + url.split("/")[2] for url in urls))


def scrape_action(scrape_urls: Iterable[str]) -> list[str]:
    assert CONTACT_PATHS
    emails: list[Iterable[str]] = []

    with HttpxBrowser() as browser:
        for url in scrape_urls:
            worker = DefaultWorker(
                url,
                browser,
                link_filter=ContactInfoLinkFilter(url, CONTACT_PATHS),
                data_extractors=[AdvancedEmailExtractor()],
            )
            data = worker.get_data()
            emails_found = [page.data["email"] for page in data if page.data["email"]]
            emails += emails_found

    return list({item for sub in emails for item in sub})


@router.post("/search-action")
def search_action_endpoint(payload: SearchPayload) -> list[str]:
    return search_action(payload.queries)


@router.post("/scrape-action")
def scrape_action_endpoint(payload: ScrapePayload) -> list[str]:
    return scrape_action(payload.urls)
