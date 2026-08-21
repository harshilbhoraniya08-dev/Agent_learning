import sys
from pathlib import Path
from typing import List

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from models import AgentOutput,FinalReport,AgentType,Plan,TaskStatus
from agents.aggregator import AggregatorAgent
from agents.planner import PlannerAgent
from agents.news import NewsAgent
from agents.research import ResearchAgent

class OrchestratorEngine:
    """ OrchestratorEngine is managing planning , task dispatching and report aggregation."""

    def __init__(self):
        self.planner = PlannerAgent()
        self.aggregator = AggregatorAgent()
        self.news_agent = NewsAgent()
        self.research_agent = ResearchAgent()

    def run(self, objective:str) -> FinalReport:
        """Executes the entire multi-agent life-cycle for given Objective."""
        print("="*40)
        print(f"[Orchestrator] Starting workflow for objective:\n'{objective}'")
        print("="*40)

        #Part 1 Planning
        print("Planning and Task decomposition")
        plan: Plan = self.planner.plan(objective)
        print(f" Generated {len(plan.tasks)} sub-tasks:")
        for t in plan.tasks:
            print(f" [{t.id}] {t.agent_type.value.upper()}: {t.description}")

        #Part 2 Worker Dispatch Phase

        print("\n Dispatching the task to specialized agents.....")
        intermediate_outputs:List[AgentOutput] = []

        for task in plan.tasks:
            task.status = TaskStatus.IN_PROGRESS

            if task.agent_type == AgentType.RESEARCH:
                output = self.research_agent.execute_task(task)
            elif task.agent_type == AgentType.NEWS:
                output = self.news_agent.execute_task(task)
            else:
                print(f"Unknown agent type: {task.agent_type}. Skipping.")
                continue

            task.status = TaskStatus.COMPLETED
            task.result = output.findings
            intermediate_outputs.append(output)

        #part 3 Final phase
        print("\n Synthesizing Final Report....")
        final_report: FinalReport = self.aggregator.aggregate(
            objective=objective,
            outputs=intermediate_outputs
        )

        return final_report

if __name__ == "__main__":
    orchestrator = OrchestratorEngine()
    test_goal = "Analyze the impact of EU AI Act on open-source AI development and community reactions."
    report = orchestrator.run(test_goal)

    print("\n" + "=" * 60)
    print("🏆 FINAL DELIVERABLE")
    print("=" * 60)
    print(f"Title: {report.title}\n")
    print(f"Executive Summary:\n{report.executive_summary}\n")
    print("Key Findings:")
    for finding in report.key_findings:
        print(f" • {finding}")
    print(f"\nSources Cited: {report.sources}")
