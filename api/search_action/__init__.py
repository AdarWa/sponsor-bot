import json
import azure.functions as func
from ddgs import DDGS


def main(req: func.HttpRequest) -> func.HttpResponse:
    body: dict = req.get_json()
    queries = body["queries"]
    
    urls = []
    
    for query in queries:
        result = DDGS().text(query, region='il-he', safesearch='off', timelimit='y', page=1, backend="auto")
        urls += [item['href'] for item in result]
    
    return func.HttpResponse(
        json.dumps(urls),
        mimetype="application/json",
        status_code=200
    )