from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import logging
import json
import re

from core.model import ResultTask

logger = logging.getLogger(__name__)

class BaseAgent(ABC):

    def __init__(self, 
                 name: str,
                 role: str,
                 system_prompt: str,
                 allowed_tools: Optional[List[str]] = None):
        
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.allowed_tools = allowed_tools or []

    @staticmethod
    def safe_parse_agent_json(raw_text: str) -> Dict[str, Any]:
        """
        Robustly parses raw LLM text into a dictionary.
        Handles unescaped newlines, markdown fences, control characters, and surrounding prose.
        """
        if not raw_text or not isinstance(raw_text, str):
            raise ValueError("Empty or invalid string provided for JSON parsing.")

        text = raw_text.strip()

        # 1. Strip Markdown Code Block Fences
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        # 2. First Attempt: Standard Strict Parsing
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 3. Second Attempt: Non-Strict Parsing (allows raw control characters like unescaped newlines)
        try:
            return json.loads(text, strict=False)
        except json.JSONDecodeError:
            pass

        # 4. Third Attempt: Regex Repair for unescaped multi-line text inside JSON values
        try:
            repaired = re.sub(
                r'(?<=: ")(.*?)(?="(,|\s*\}))',
                lambda m: m.group(1).replace('\n', '\\n').replace('\r', '').replace('\t', '\\t'),
                text,
                flags=re.DOTALL
            )
            return json.loads(repaired, strict=False)
        except Exception:
            pass

        # 5. Final Fallback: Extract JSON object via regex if there is surrounding conversational text
        json_match = re.search(r'(\{.*\})', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1), strict=False)
            except Exception:
                pass

        raise ValueError(f"Output could not be parsed into valid JSON: {raw_text[:100]}...")

    def parse_response(self, raw_llm_output: str) -> Dict[str, Any]:
        """
        Helper method to parse raw agent responses with built-in logging and fallback handling.
        """
        try:
            return self.safe_parse_agent_json(raw_llm_output)
        except ValueError as e:
            logger.warning(f"[{self.name}] Safe JSON parsing fallback triggered: {e}")
            return {
                "thought": "Failed to parse structured JSON from model response.",
                "final_answer": raw_llm_output
            }

    @abstractmethod
    async def run(self, task: str, task_id: Optional[str] = None) -> ResultTask:
        """
        Main execution contract for processing a task.

        Parameters:
            task (str): Task description or instruction prompt.
            task_id (Optional[str]): Unique task tracking ID in graph executions.

        Returns:
            ResultTask: Standardized system output container.
        """
        pass

    def get_metadata(self) -> Dict[str, Any]:
        """Exposes capability metadata for coordinator discovery."""
        return {
            "name": self.name,
            "role": self.role,
            "allowed_tools": self.allowed_tools
        }