import os

import httpx
from fastapi import HTTPException
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

# from backend.app.utils.env_util import load_environment
# from backend.app.utils.logger_util import log_debug

try:
    from ddgs.exceptions import DDGSException
except ImportError:
    DDGSException = Exception


# @tool("Search the web for relevant information", return_direct=True)
def tool_search_web(query: str, region: str = "in-en") -> list:
    """
    Tool to search the web using the provided query.
    :param query:
    :param region: Region code for DuckDuckGo search (default is "in" for India)
    :return:
    """
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context

    wrapper = DuckDuckGoSearchAPIWrapper(region=region, max_results=5,safesearch="on")
    search = DuckDuckGoSearchResults(output_format="list", api_wrapper=wrapper)

    try:
        response = search.invoke(query)
    except DDGSException as e:
        print(f"DuckDuckGo search failed for query '{query}': {e}")
        return []
    except Exception as e:
        print(f"Unexpected error during web search for query '{query}': {e}")
        return []

    return response


# async def search_web_tool(query: str) -> dict:
#     """
#     Calls Google Custom Search API to search the web.

#     Args:
#         query: The search query string

#     Returns:
#         dict: Search results from Google Custom Search API
#     """
#     # load_environment('environment/.env.other')
#     api_key = os.getenv("SEARCH_KEY")  # Store in environment variable
#     cx = "a155314d3a0ae4113"

#     url = "https://www.googleapis.com/customsearch/v1"
#     params = {
#         "key": api_key,
#         "cx": cx,
#         "q": query
#     }

#     try:
#         async with httpx.AsyncClient() as client:
#             response = await client.get(url, params=params)
#             response.raise_for_status()
#             return response.json()
#     except httpx.HTTPStatusError as e:
#         raise HTTPException(status_code=e.response.status_code, detail=str(e))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")