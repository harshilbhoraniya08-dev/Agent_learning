# config.py
import os
from pathlib import Path
from dotenv import load_dotenv

ENV_FILE = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_FILE, override=True)


class Settings:
    """Central configuration using direct environment loading."""
    
    def __init__(self):
        # Retrieve credentials
        self.NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "").strip()
        self.NVIDIA_BASE_URL: str = os.getenv(
            "NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"
        ).strip()

        # Model configurations
        self.DEFAULT_MODEL: str = os.getenv(
            "DEFAULT_MODEL", "meta/llama-3.3-70b-instruct"
        ).strip()
        self.FAST_MODEL: str = os.getenv(
            "FAST_MODEL", "meta/llama-3.1-8b-instruct"
        ).strip()

        # Runtime safeguards
        self.REQUEST_TIMEOUT: float = float(os.getenv("REQUEST_TIMEOUT", "90.0"))
        self.MAX_LOOPS: int = int(os.getenv("MAX_LOOPS", "5"))

        # Explicit startup validation
        self._validate()

    def _validate(self):
        """Ensures critical credentials are present before system starts."""
        if not self.NVIDIA_API_KEY:
            raise ValueError(
                f"\n[Config Error]: NVIDIA_API_KEY is missing or empty.\n"
                f"Checked .env file at: {ENV_FILE}\n"
                f"Please ensure your .env has: NVIDIA_API_KEY=nvapi-..."
            )


# Singleton settings instance
settings = Settings()
