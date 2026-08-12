import asyncio
from typing import List, Optional,Dict,Any
from core.model import Plan, AgentTask, ResultTask
import logging 
from Agents.base_agent import BaseAgent
from orchestration.dependency_engine import DependencyEngine
from orchestration.planner import Planner

logger = logging.getLogger(__name__)

class Coordinator:
    """"
    Multi-Agent Orchestrator: Orchestrates the execution of a Plan by coordinating multiple specialized agents
    """

    def __init__(self, agent_pool: Dict[str, BaseAgent],default_agent: BaseAgent):
        self.agent_pool = agent_pool
        self.default_agent = default_agent

    def _prepare_task(self, task: AgentTask, completed_results: Dict[str, ResultTask]) -> str:
        if not task.depends_on:
            return task.task
        context_block = [f"Task Objective: {task.task}\n\nContext from Prior Completed Tasks:"]

        for dep_id in task.depends_on:
            result_obj = completed_results.get(dep_id)
            if result_obj and result_obj.result:
                context_block.append(f"--- Output from Dependency [{dep_id}]-- \n{result_obj.result}")
            elif result_obj and result_obj.error:
                context_block.append(f"--- Error from Dependency [{dep_id}]-- \n{result_obj.error}")
        return "\n\n".join(context_block)

    async def _execute_single_task(self, task:AgentTask, completed_tasks: Dict[str,ResultTask]) -> ResultTask:
        """
        Routes an individual task to appropriate agent for execution and to its baseagents instence
        """
        agent = self.agent_pool.get(task.assigned_agent,self.default_agent)

        task_prompt_with_context = self._prepare_task(task, completed_tasks)

        logger.info(f"[Coordinator] Dispatching '{task.id}' to Agent '{agent.name}' ({agent.role})")
        return await agent.run(task = task_prompt_with_context, task_id=task.id)

    async def run_plan(self, plan: Plan) -> Dict[str, ResultTask]:
        """"
        Execute a complete plan by resolving dependencies and dispatching tasks to appropriate agents.
        """
        logger.info(f"[Coordinator] Starting execution of plan for objective: '{plan.objective}'")

        batches = DependencyEngine.resolve_execution_batches(plan)
        completed_results:Dict[str, ResultTask] = {}

        #2 : Iterate through each batch sequentially
        for batch_index, batch in enumerate(batches, start=1):
            logger.info(f"[Coordinator] --- Executing Batch {batch_index}/{len(batches)} ({len(batch)} task(s)) ---")
            async_tasks = [
                self._execute_single_task(task, completed_results) 
                for task in batch 
            ]

            batch_results : List[ResultTask] = await asyncio.gather(*async_tasks, return_exceptions=False)

            #4: Stor result of completed tasks in completed_results dictionary
            for res in batch_results:
                completed_results[res.task_id] = res
                if res.error:
                    logger.error(f"[Coordinator] Task '{res.task_id}' failed with error: {res.error}")
                else:
                    logger.info(f"[Coordinator] Task '{res.task_id}' completed successfully.")
        logger.info(f"[Coordinator] Plan execution completed for objective: '{plan.objective}'")
        return completed_results




       