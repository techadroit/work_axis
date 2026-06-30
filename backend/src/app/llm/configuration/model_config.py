from dataclasses import dataclass

# Context Management Constants
LOOP_DETECTION_MIN_CALLS = 5
LOOP_DETECTION_MAX_UNIQUE_TOOLS = 2
MAX_ITERATION_COUNT = 15
MAX_CONTEXT_CHARS = 100000  # Rough estimate: 100k chars ≈ 25k tokens
MAX_MESSAGES_HISTORY = 20
MAX_TOOL_RESULT_LENGTH = 2000
MAX_TOOLS_PER_ITERATION = 5

@dataclass
class ModelConfig:
    temperature: float = 0.5
    top_p: float = 1.0
    max_tokens: int = 4000
    timeout: int = None
    max_retries: int = 2
