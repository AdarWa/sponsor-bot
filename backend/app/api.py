import requests

class ScrapeApi:
    
    def __init__(self, base_url: str, api_key: str) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"x-functions-key": self.api_key})
        
    def scrape_website(self, site: str) -> dict:
        response = self.session.post(
            self.base_url + "/scrape-action",
            json={
                "url":site
            }
        )
        
        response.raise_for_status()
        return response.json()