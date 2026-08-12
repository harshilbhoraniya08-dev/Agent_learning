import logging
from typing import Any, Dict, List,Set
from core.model import Plan, AgentTask

logger = logging.getLogger(__name__)

class DependencyEngine:

    @staticmethod
    def resolve_execution_batches(plan: Plan) -> List[List[AgentTask]]:
        """
        Resolve the execution batches for the given plan.
        """
        logger.info(f"[DependencyEngine] Resolving DAG for objective: '{plan.objective}'")
        tasks_by_id: Dict[str, AgentTask] = {task.id: task for task in plan.tasks}
        completed_tasks: Set[str] = set()
        unresolved_tasks: Set[str] = set(tasks_by_id.keys())
        execution_batches:List[List[AgentTask]] = []

        while unresolved_tasks:

            current_batch: List[AgentTask] = []

            for task_id in list(unresolved_tasks):
                task = tasks_by_id[task_id]
                if all(dep_id in completed_tasks for dep_id in task.depends_on):
                    current_batch.append(task)

            if not current_batch:
                logger.error(f"[DependencyEngine]  Circular dependency deadlock detected!"
                             f"Unresolved tasks: {unresolved_tasks}")
                remaining_tasks= [tasks_by_id[tid] for tid in unresolved_tasks]
                execution_batches.append(remaining_tasks) 
                break

            for task in current_batch:
                completed_tasks.add(task.id)
                unresolved_tasks.remove(task.id)

            execution_batches.append(current_batch)
            logger.info(f"[DependenecyEngine] Created Batch {len(execution_batches)}"
                        f"with {len(current_batch)} tasks. Remaining unresolved tasks: {len(unresolved_tasks)}")
        return execution_batches