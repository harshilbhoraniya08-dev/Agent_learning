import json 
import logging
from typing import Dict, Any, Optional
from core.config import config
from governance.memory_manager import MemoryManager        
from core.model import ResultTask
from core.llm import call_llm

logger = logging.getLogger(__name__)

SUPERVISIOR_SYSTEM_PROMPT = """
You are the Senior AI System Supervisor and Quality Auditor.
Your responsibility is to review the results produced by specialized sub-agents, evaluate whether the user's objective was achieved, and synthesize a polished, unified final response.

Original Objective:
{objective}

Execution Results from Agents:
{agent_results}

Instructions:
1. Carefully review all completed task outputs.
2. Evaluate if there were any task failures or missing data points.
3. Synthesize the findings into a cohesive, structured, professional final deliverable that directly answers the original objective.
4. Do NOT simply list task outputs raw—combine them into a well-written single response.
5. If partial information is missing due to a task error, explicitly acknowledge the limitation gracefully.

Return ONLY the final synthesized report directly.
"""

class Supervisor:
    def __init__(self, memory_manager: Optional[MemoryManager]=None):
        self.memory = memory_manager or MemoryManager()

    def _format_task_results(self, results: Dict[str, ResultTask]) -> str:
        formatted_blocks=[]
        for task_id, res in results.items():
            self.memory.record_result(res)
            status = "Success" if not res.error else f"Failed : {res.error}"
            formatted_blocks.append(
                "### Sub-Task: {task_id}\n"
                f"- Assigned Agent: {res.agent}\n"
                f"- Execution Status: {status}\n"
                f"- Output Payload:\n{res.result or 'No output returned.'}"
            )
        return "\n\n".join(formatted_blocks)

    async def evaluate_and_synthesize(self, objective: str, results: Dict[str, ResultTask])->str:

        logger.info(f"[Supervisor] Synthesizing final results for objective: '{objective}'")

        formatted_results = self._format_task_results(results)
        system_prompt = SUPERVISIOR_SYSTEM_PROMPT.format(
            objective=objective,
            agent_results=formatted_results
        )

        messages = [
            {"role":"system", "content": system_prompt},
            {"role": "user", "content": f"Please generate the final synthesized response for objective: '{objective}'"}
        ]

        try:
            synthesized_output = await call_llm(messages)
            logger.info("[Supervisor] Successfully synthesized final deliverable.")
            return (synthesized_output or "").strip()
        except Exception as e:
            logger.error(f"[Supervisor] Failed during output synthesis: {str(e)}")
            fallback_output = f"# Final Output (Raw Fallback)\nObjective: {objective}\n\n"
            for task_id, res in results.items():
                fallback_output += f"## {task_id} ({res.agent})\n{res.result or res.error}\n\n"
            return fallback_output
        

