import logging
import aiohttp
import asyncio

async def scrape_emails_via_azure(urls: list[str], azure_function_url: str) -> list[str]:
    """
    Calls an Azure Function to scrape emails from a website.
    
    Args:
        url: The website URL to scrape
        azure_function_url: The Azure Function endpoint URL
        
    Returns:
        List of emails found on the website
    """
    payload = {"urls": urls}
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(azure_function_url, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("emails", [])
                else:
                    logging.error(f"Error: Azure Function returned status {response.status}")
                    return []
        except asyncio.TimeoutError:
            logging.error("Email scrape request failed - timed out;")
            return []
        except aiohttp.ClientError as e:
            logging.error(f"Request failed: {e}")
            return []