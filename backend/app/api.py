import asyncio
import aiohttp
from typing import Iterable

from backend.app.utils import Singleton

BATCH_SIZE = 5


class ScrapeApi(Singleton):

    async def init(self, base_url: str, api_key: str | None = None) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.session = aiohttp.ClientSession(
            headers={"x-functions-key": api_key} if api_key else {}
        )

    async def _post_batches(
        self,
        endpoint: str,
        payload_key: str,
        items: Iterable[str],
    ) -> list[str]:
        results: list[str] = []

        async def post_batch(batch: list[str]) -> None:
            async with self.session.post(
                f"{self.base_url}/{endpoint}",
                json={payload_key: batch},
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    results.extend(data)

        tasks = [
            post_batch(list(items)[i:i + BATCH_SIZE])
            for i in range(0, len(list(items)), BATCH_SIZE)
        ]

        await asyncio.gather(*tasks, return_exceptions=True)
        return results

    async def scrape_website(self, sites: str | list[str]) -> list[str]:
        urls = [sites] if isinstance(sites, str) else sites
        return await self._post_batches(
            endpoint="scrape-action",
            payload_key="urls",
            items=urls,
        )

    async def scrape_search(self, queries: str | list[str]) -> list[str]:
        qs = [queries] if isinstance(queries, str) else queries
        return await self._post_batches(
            endpoint="search-action",
            payload_key="queries",
            items=qs,
        )

    async def close(self) -> None:
        if self.session and not self.session.closed:
            await self.session.close()
