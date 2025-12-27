from __future__ import annotations
import json
import azure.functions as func
from extract_emails import DefaultWorker
from extract_emails.browsers import HttpxBrowser
from extract_emails.link_filters import ContactInfoLinkFilter
from .scraper.scraper import urls
from .scraper.email_data_extractor import EmailExtractor


def main(req: func.HttpRequest) -> func.HttpResponse:
    body: dict = req.get_json()
    scrape_urls = body["urls"]
    assert urls
    emails = []
    with HttpxBrowser() as browser:
        for url in scrape_urls:
            worker = DefaultWorker(url, browser, link_filter=ContactInfoLinkFilter(url,urls), data_extractors=[EmailExtractor()])
            data = worker.get_data()
            emails_found = [page.data["email"] for page in data if page.data["email"]]
            emails += emails_found
        
    return func.HttpResponse(
        json.dumps(list({item for sub in emails for item in sub})),
        mimetype="application/json",
        status_code=200
    )