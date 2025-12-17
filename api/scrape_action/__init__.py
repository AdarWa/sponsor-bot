import json
import azure.functions as func
from extract_emails import DefaultWorker
from extract_emails.browsers import HttpxBrowser
from extract_emails.link_filters import ContactInfoLinkFilter
from .scraper.scraper import urls
from .scraper.email_data_extractor import EmailExtractor

def main(req: func.HttpRequest) -> func.HttpResponse:
    body: dict = req.get_json()
    url = body["url"]
    assert url
    with HttpxBrowser() as browser:
        worker = DefaultWorker(url, browser, link_filter=ContactInfoLinkFilter(url,urls), data_extractors=[EmailExtractor()])
        data = worker.get_data()
        dict_data = [page.model_dump() for page in data if page.data["email"]]
        return func.HttpResponse(
            json.dumps(dict_data)
        )