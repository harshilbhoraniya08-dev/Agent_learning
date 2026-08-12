import logging
from typing import Dict, Any , List,Optional
from core.model import ResultTask

logger = logging.getLogger(__name__)

class MemoryManager:
    """
    Pillar 5 (Memory & Governance): State Persistence & Context Memory Engine.
    """

    def __init__(self, max_history_items:int=20):
        self.max_history_items = max_history_items
        self._key_value_store:Dict[str, Any] = {}
        self._task_history:List[ResultTask] = []

    def set_state(self, key:str, value:Any) -> None:
        """store Global system state in memory"""
        self._key_value_store[key] = value
        logger.debug(f"[MemoryManager] Set state: {key}")

    def get_state(self, key:str, default:Any=None) -> Any:
        """Retrieves a global system state from memory"""
        return self._key_value_store.get(key, default)

    def record_result(self, result_task:ResultTask) -> None:
        """Records a completed task result in the task history"""
        self._task_history.append(result_task)

        # Trim oldest entries when exceeding max history
        if len(self._task_history) > self.max_history_items:
            removed = self._task_history.pop(0)
            logger.debug(f"[MemoryManager] memory buffer full, removed: {removed}")

        logger.info(f"[MemoryManager] Recorded result: {result_task}")

    def get_history(self) -> List[ResultTask]:
        """Returns all recorded task execution histories."""
        return self._task_history.copy()

    def format_history_context(self, last_n: Optional[int] = None) -> str:
        """
        Formats recorded task execution history into a clean context string
        suitable for LLM prompts.
        """
        records = self._task_history[-last_n:] if last_n else self._task_history
        if not records:
            return "No previous execution history available."

        formatted_blocks = []
        for record in records:
            status = "SUCCESS" if not record.error else f"FAILED ({record.error})"
            formatted_blocks.append(
                f"Task ID: {record.task_id}\n"
                f"Agent: {record.agent}\n"
                f"Status: {status}\n"
                f"Output: {record.result or 'None'}"
            )

        return "\n\n---\n\n".join(formatted_blocks)

    def clear(self) -> None:
        """Resets all stored state and task history."""
        self._key_value_store.clear()
        self._task_history.clear()
        logger.info("[MemoryManager] Cleared all stored memory state.")
    

