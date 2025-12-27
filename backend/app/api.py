import aiohttp

from backend.app.utils import Singleton

class ScrapeApi(Singleton):

    async def init(self, base_url: str, api_key: str | None = None) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.session = aiohttp.ClientSession(
            headers={"x-functions-key": self.api_key} if self.api_key else {}
        )

    async def scrape_website(self, sites: str | list[str]) -> list[str]:
        urls = [sites] if isinstance(sites, str) else sites
        async with self.session.post(
            f"{self.base_url}/scrape-action",
            json={"urls": urls}
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def close(self) -> None:
        if self.session:
            await self.session.close()
