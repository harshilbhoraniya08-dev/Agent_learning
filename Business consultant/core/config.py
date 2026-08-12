from dataclasses import dataclass
import os
from dotenv import load_dotenv


load_dotenv()



@dataclass
class Config:

    # ==================
    # LLM Configuration
    # ==================

    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")

    BASE_URL: str = os.getenv(
        "BASE_URL",
        "https://openrouter.ai/api/v1"
    )

    MODEL: str = os.getenv(
        "MODEL",
        "openrouter/free"
    )

    TEMPERATURE: float = 0.2

    MAX_TOKENS: int = 2000



    # ==================
    # Agent Configuration
    # ==================

    MAX_REACT_STEPS: int = 5

    MAX_RETRIES: int = 3

    AGENT_TIMEOUT: int = 60



    # ==================
    # Search Tool
    # ==================

    DEFAULT_SEARCH_RESULTS: int = 5



    # ==================
    # Logging
    # ==================

    DEBUG: bool = True

    VERBOSE: bool = True

config = Config()
if not config.OPENROUTER_API_KEY:
    raise ValueError(
        "OPENROUTER_API_KEY not found in environment"
    )