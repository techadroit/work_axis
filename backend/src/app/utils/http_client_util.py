"""
HTTP Client Configuration with SSL Support
Configures httpx and requests libraries for secure API calls
"""
import os
from typing import Optional

from infra.local.ssl_config import get_client_ssl_context
from src.app.utils.logger_util import log_info, log_error


def log_warning(message):
    """Log warning using log_error with WARNING prefix"""
    log_error(f"WARNING: {message}")


def create_httpx_client(verify_ssl: Optional[bool] = None, timeout: float = 30.0):
    """
    Create an httpx client with proper SSL configuration

    Args:
        verify_ssl: Whether to verify SSL certificates (None = auto-detect from env)
        timeout: Request timeout in seconds

    Returns:
        Configured httpx AsyncClient
    """
    import httpx

    if verify_ssl is None:
        # Check environment variable
        verify_ssl = os.getenv("VERIFY_SSL", "true").lower() == "true"

    if not verify_ssl:
        log_warning("SSL verification is disabled for HTTP clients. Not recommended for production!")

    # Create SSL context
    ssl_context = get_client_ssl_context(verify=verify_ssl)

    # Create client with SSL configuration
    client = httpx.AsyncClient(
        verify=verify_ssl if verify_ssl else False,
        timeout=timeout,
    )

    log_info(f"Created httpx client with SSL verification: {verify_ssl}")
    return client


def create_requests_session(verify_ssl: Optional[bool] = None, timeout: float = 30.0):
    """
    Create a requests session with proper SSL configuration

    Args:
        verify_ssl: Whether to verify SSL certificates (None = auto-detect from env)
        timeout: Request timeout in seconds

    Returns:
        Configured requests Session
    """
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

    if verify_ssl is None:
        # Check environment variable
        verify_ssl = os.getenv("VERIFY_SSL", "true").lower() == "true"

    if not verify_ssl:
        log_warning("SSL verification is disabled for HTTP clients. Not recommended for production!")
        # Disable urllib3 warnings about insecure requests
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Create session
    session = requests.Session()

    # Configure retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"]
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # Set SSL verification
    session.verify = verify_ssl

    log_info(f"Created requests session with SSL verification: {verify_ssl}")
    return session


def configure_ssl_for_apis():
    """
    Configure SSL settings for all API calls in the application
    Call this during application startup
    """
    # Set default SSL verification from environment
    verify_ssl = os.getenv("VERIFY_SSL", "true").lower() == "true"

    log_info("Configuring SSL for API calls...")
    log_info(f"SSL Verification: {verify_ssl}")

    # Set environment variables for libraries that respect them
    if not verify_ssl:
        os.environ["CURL_CA_BUNDLE"] = ""
        os.environ["REQUESTS_CA_BUNDLE"] = ""
        log_warning("SSL verification disabled globally")

    return verify_ssl


# Example usage for LangChain integrations
def get_langchain_llm_kwargs() -> dict:
    """
    Get common kwargs for LangChain LLM clients with SSL configuration

    Returns:
        Dictionary of kwargs to pass to LangChain LLM constructors
    """
    verify_ssl = os.getenv("VERIFY_SSL", "true").lower() == "true"

    kwargs = {
        "timeout": 30.0,
        "max_retries": 3,
    }

    # Note: http_client configuration is provider-specific
    # Some providers support custom httpx clients
    # Configure per provider as needed

    return kwargs


if __name__ == "__main__":
    # Test SSL configuration
    configure_ssl_for_apis()

    # Test httpx client
    import asyncio

    async def test():
        client = create_httpx_client()
        try:
            response = await client.get("https://httpbin.org/get")
            print(f"HTTPX Test: Status {response.status_code}")
        finally:
            await client.aclose()

    # asyncio.run(test())

    # Test requests session
    # session = create_requests_session()
    # response = session.get("https://httpbin.org/get")
    # print(f"Requests Test: Status {response.status_code}")

