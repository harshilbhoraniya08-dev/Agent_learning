import json
import logging
from Agents.base_agent import BaseAgent
from typing import Optional,List,Dict,Any
from core.config import config
from core.llm import call_llm
from core.model import ResultTask,Action,Thought,Observation,AgentTask,Plan
from Tools.tool_executor import execute_tool
from Tools.tool_registery import get_tool_schemas   


logger = logging.getLogger(__name__)

PLANNER_SYSTEM_PROMPT = """You are an expert AI System Architect and Task Planner.
                    Your job is to break down a high-level user objective into a structured sequence of clear, executable sub-tasks for specialized AI agents.

                    Available Agent Roles & Capabilities:
                    {available_agents}

                    Instructions:
                    1. Deconstruct the objective into atomic, non-overlapping sub-tasks.
                    2. Assign each task to the most appropriate agent role available.
                    3. Define strict dependencies between tasks using 'dependencies' (list of task_ids that must finish before this task can start).
                    4. Tasks with no dependencies can run in parallel.

                    You must respond ONLY with a valid JSON object strictly matching this schema:
                    {{
                      "objective": "The original user objective",
                      "tasks": [
                        {{
                          "task_id": "task_1",
                          "description": "Clear description of what this specific step must accomplish",
                          "assigned_agent": "Exact role name of the agent assigned",
                          "dependencies": []
                        }},
                        {{
                          "task_id": "task_2",
                          "description": "Second step description...",
                          "assigned_agent": "Exact role name...",
                          "dependencies": ["task_1"]
                        }}
                      ]
                    }}
                    
                    Do not include markdown blocks outside the JSON, commentary, or conversational fluff."""

class Planner:
    """
    Deconstructs high-level objectives into executable AgentTask DAG structure.
    """

    def __init__(self, available_agents:Optional[List[Dict[str, str]]] = None):
        self.available_agents = available_agents or [
            {"role": "Researcher", "description": "Searches for information, gathers facts, and summarizes raw data."},
            {"role": "Analyst", "description": "Evaluates data, identifies trends, and performs comparison logic."},
            {"role": "Writer", "description": "Synthesizes reports, writes documentation, and creates polished final deliverables."}
        ]

    def _format_agents_prompt(self) -> str:
        formatted = []
        for agent in self.available_agents:
            formatted.append(f"- Role: '{agent['role']}' | Capability: {agent['description']}")
        return "\n".join(formatted)
    
    async def create_plan(self, objective:str) -> Plan:
        """
        invocates the planner llm to transform an objective string into a Plan Object.
        """
        logger.info(f"[Planner] Generating task decomposition plan for : '{objective}")
        system_prompt = PLANNER_SYSTEM_PROMPT.format(
            available_agents=self._format_agents_prompt()
        )

        messages = [
            {"role": "system", "content":system_prompt},
            {"role": "user", "content":f"Objective: {objective  }"}
        ]

        try:
            response_str = await call_llm(messages)
            if not response_str:
                raise ValueError("Planner LLM returned empty response")
            cleaned_response = response_str.strip()
            if cleaned_response.startswith("'''json"):
                cleaned_response = cleaned_response[7:-3].strip()
            elif cleaned_response.startswith("'''"):
                cleaned_response = cleaned_response[3:-3].strip()

            plan_dict = json.loads(cleaned_response)

            #convert the dictionary to pydantic models
            tasks = [
                AgentTask(
                    id = t["task_id"],
                    task=t["description"],
                    assigned_agent=t.get("assigned_agent","Researcher"),
                    depends_on = t.get("dependencies", [])
                )
                for t in plan_dict.get("tasks", [])
            ]

            plan = Plan(
                objective=plan_dict.get("objective", objective),
                tasks=tasks
            )
            logger.info(f"[Planner] plan generated successfully with {len(plan.tasks)} sub-tasks")
            return plan
        
        except (json.JSONDecodeError,KeyError) as e:
            logger.error(f"[Planner] Failed to parse generated plan into standard schema: {str(e)}")
            #Fallback single-task plan if parsing fails
            fallback_task = AgentTask(
                id = "task_fallback_1",
                task=objective,
                assigned_agent="Generalist",
                depends_on=[]
            )

            return Plan(objective=objective, tasks=[fallback_task])
        except Exception as e:
            logger.error(f"[Planner] Critical error during planning phase : {str(e)}")
            raise e

