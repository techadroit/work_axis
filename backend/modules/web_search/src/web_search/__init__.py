from .local.web_search_tool import tool_search_web
from .local.web_content_extraction import tool_extract_webpage_content

__all__ = ["tool_search_web", "tool_extract_webpage_content"]


def main() -> None:
    print("web-search module is installed and ready")
