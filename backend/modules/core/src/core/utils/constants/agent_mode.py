from enum import Enum


class AgentMode(str, Enum):
    DOCUMENT = "document"
    WEBSEARCH = "websearch"
    AGENT = "agent"
    OFFLINE = "offline"
