import logging
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Scrape action HTTP trigger processed a request.")

    name = req.params.get("name")
    if not name:
        try:
            body = req.get_json()
        except ValueError:
            body = {}
        name = body.get("name")

    if not name:
        return func.HttpResponse(
            "Pass a name in the query string or request body.",
            status_code=400,
        )

    return func.HttpResponse(f"Hello, {name}! Function executed successfully.")
