import json
import logging
from typing import Optional, List, Dict, Any

from Agents.base_agent import BaseAgent
from core.config import config
from core.llm import call_llm
from core.model import ResultTask, Action, Thought, Observation
from Tools.tool_executor import execute_tool
from Tools.tool_registery import get_tool_schemas

logger = logging.getLogger(__name__)


REACT_SYSTEM_PROMPT = """You are a specialized AI Agent operating in a ReAct (Reason + Act) loop.
Your Role: {role}
Agent Name: {name}

Instructions:
{system_prompt}

You have access to the following tools:
{tool_schemas}

To use a tool, format your output strictly as a JSON object matching this structure:
{{
  "thought": "Reasoning step explaining what you want to do next",
  "action": {{
    "tool_name": "name_of_tool",
    "tool_input": {{ "param1": "value1" }}
  }}
}}

If you have all the information required to give the final answer, format your output strictly as:
{{
  "thought": "Reasoning step explaining why you are finished",
  "final_answer": "Your complete, accurate final answer here"
}}

IMPORTANT: Return ONLY valid, parseable JSON. Do not include markdown codeblocks or conversational text outside the JSON object.
"""


class ReActAgent(BaseAgent):
    """
    Autonomous ReAct Reasoning Engine implementing the BaseAgent interface.

    Architectural Purpose:
    - Executes an iterative Thought -> Action -> Observation loop.
    - Limits execution using strict step bounds (MAX_REACT_STEPS).
    - Filters available tool schemas based on allowed_tools security boundaries.
    - Returns standardized ResultTask data containers.
    """

    def __init__(
        self,
        name: str,
        role: str,
        system_prompt: str,
        allowed_tools: Optional[List[str]] = None
    ):
        super().__init__(name, role, system_prompt, allowed_tools)
        self.tool_schemas = self._get_filtered_schemas()

    def _get_filtered_schemas(self) -> List[Dict[str, Any]]:
        """Extracts JSON schemas only for tools explicitly allowed for this agent."""
        all_schemas = get_tool_schemas()
        if not self.allowed_tools:
            return []
        
        return [
            schema for schema in all_schemas 
            if schema["function"]["name"] in self.allowed_tools
        ]

    async def run(self, task: str, task_id: Optional[str] = None) -> ResultTask:
        """
        Executes the ReAct loop asynchronously until completion or max steps reached.
        """
        task_id = task_id or f"task_{self.name}_001"
        logger.info(f"[{self.name}] Starting task execution: '{task}'")

        # 1. Format System Context
        formatted_system_prompt = REACT_SYSTEM_PROMPT.format(
            name=self.name,
            role=self.role,
            system_prompt=self.system_prompt,
            tool_schemas=json.dumps(self.tool_schemas, indent=2)
        )

        messages = [
            {"role": "system", "content": formatted_system_prompt},
            {"role": "user", "content": task}
        ]

        step_count = 0

        # 2. ReAct Iteration Loop
        while step_count < config.MAX_REACT_STEPS:
            step_count += 1
            logger.info(f"[{self.name}] ReAct Loop Step {step_count}/{config.MAX_REACT_STEPS}")

            response_str = ""
            try:
                # LLM Call
                response_str = await call_llm(messages)
                response_str = response_str or ""

                # Sanitize potential codeblock formatting in response
                cleaned_response = str(response_str).strip()
                if cleaned_response.startswith("```json"):
                    cleaned_response = cleaned_response[7:-3].strip()
                elif cleaned_response.startswith("```"):
                    cleaned_response = cleaned_response[3:-3].strip()

                response_json = json.loads(cleaned_response)

            except json.JSONDecodeError as e:
                # Failure Recovery: Instruct LLM to correct JSON format on next pass
                error_msg = f"Invalid JSON format output by agent. Raw output was: '{response_str}'. Error: {str(e)}"
                logger.warning(f"[{self.name}] {error_msg}")
                messages.append({"role": "assistant", "content": str(response_str or "")})
                messages.append({"role": "user", "content": "Your response was not valid JSON. Please return ONLY a valid JSON object matching the required schema."})
                continue

            except Exception as e:
                logger.error(f"[{self.name}] Critical LLM invocation error: {str(e)}")
                return ResultTask(
                    task_id=task_id,
                    agent=self.name,
                    result=None,
                    error=f"LLM Invocation Failed: {str(e)}"
                )

            # Log Agent Thought
            thought_text = response_json.get("thought", "No thought provided.")
            thought = Thought(reasoning=thought_text)
            logger.info(f"[{self.name}] Thought: {thought.reasoning}")

            # 3. Check for Termination Condition (Final Answer)
            if "final_answer" in response_json:
                final_output = response_json["final_answer"]
                logger.info(f"[{self.name}] ReAct Loop Completed. Final answer generated.")
                return ResultTask(
                    task_id=task_id,
                    agent=self.name,
                    result=final_output,
                    error=None
                )

            # 4. Process Action & Tool Execution
            action_dict = response_json.get("action")
            if not action_dict or "tool_name" not in action_dict:
                # Invalid action structure feedback
                messages.append({"role": "assistant", "content": json.dumps(response_json)})
                messages.append({"role": "user", "content": "Missing 'action' or 'final_answer' field in JSON. Please decide on a tool action or provide final_answer."})
                continue

            action = Action(
                tool_name=action_dict["tool_name"],
                tool_input=action_dict.get("tool_input", {})
            )

            # Security Check: Ensure tool is in allowed list
            if self.allowed_tools and action.tool_name not in self.allowed_tools:
                obs_text = f"Security Error: Agent '{self.name}' is not allowed to execution tool '{action.tool_name}'."
            else:
                # Safe Circuit-Breaker Tool Execution
                tool_result = await execute_tool(action.tool_name, action.tool_input)
                obs_text = json.dumps(tool_result)

            observation = Observation(result=obs_text)
            logger.info(f"[{self.name}] Action: {action.tool_name} | Observation: {obs_text[:150]}...")

            # 5. Append Conversation State for Next Iteration
            messages.append({"role": "assistant", "content": json.dumps(response_json)})
            messages.append({"role": "user", "content": f"Observation: {observation.result}"})

        # Step Limit Exceeded Safeguard
        fallback_msg = f"Task exceeded maximum allowed ReAct steps ({config.MAX_REACT_STEPS}). Execution terminated."
        logger.warning(f"[{self.name}] {fallback_msg}")
        return ResultTask(
            task_id=task_id,
            agent=self.name,
            result=None,
            error=fallback_msg
        )