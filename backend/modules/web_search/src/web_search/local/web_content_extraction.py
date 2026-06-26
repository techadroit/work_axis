import asyncio

import httpx
from bs4 import BeautifulSoup

# from backend.app.utils.logger_util import log_debug


# @tool("extract content from a webpage", return_direct=True)
def tool_extract_webpage_content(url: str):
    """
    Tool to extract content from a webpage using the provided URL.
    Pass a web url to extract the content
    :param url:
    :return:
    """
    response = asyncio.run(extract_webpage_content(url))
    print("extract webpage content tool")
    print("URL: " + url)
    return response


async def extract_webpage_content(url: str, max_length: int = 5000) -> dict:
    """
    Extracts text content from a webpage.

    Args:
        url: The webpage URL to scrape
        max_length: Maximum characters to return (to avoid overwhelming context)

    Returns:
        dict: Contains url, title, and extracted text content
    """
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            # Get title
            title = soup.title.string if soup.title else ""
            # Extract text
            text = soup.get_text(separator=' ', strip=True)
            # Clean up whitespace
            text = ' '.join(text.split())
            # Truncate if too long
            if len(text) > max_length:
                text = text[:max_length] + "..."

            response = {
                "url": url,
                "title": title,
                "content": text,
                "success": True
            }

            return response

    except Exception as e:
        return {
            "url": url,
            "error": str(e),
            "success": False
        }