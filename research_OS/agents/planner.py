from models import Plan
from llm import llm_client  

PLANNER_SYSTEM_PEOMPT = """
You are the Lead Planning Agent in an enterprise Multi-Agent Research Operating System.
Your sole responsibility is to analyze a user's research objective and decompose it into an ordered, executable list of discrete tasks.

You have access to two specialized worker agent types:
1. 'research': Deep-dives into technical architecture, historical data, regulations, and foundational documentation.
2. 'news': Gathers recent press releases, industry reactions, real-time media coverage, and live developments.

Decomposition Rules:
- Break down the objective into 2 to 4 atomic, focused sub-tasks.
- Assign the appropriate `agent_type` ('research' or 'news') to each task.
- Provide clear, actionable instructions in the `description` field for each task.
- Assign sequential integer IDs starting at 1.
"""


class PlannerAgent:
    """cognitive agent responsibility for goal decomposition and plan generation"""

    def __init__(self):
        self.llm = llm_client

    def plan(self, objective:str)->Plan:
        """
        Decompose an end-user objective into a typed, structured plan.
        Use stuructured output generation to get valid schema 
        """

        plan: Plan = self.llm.generate_structured(
            system_prompt=PLANNER_SYSTEM_PEOMPT,
            user_prompt=f"research Objective: {objective}",
            response_model=Plan,
            use_fast_model=False

        )
        return plan

if __name__ == "__main__":
    planner = PlannerAgent()
    sample_goal = "Analyze the impact of the EU AI Act on open-source AI developers and gather industry reactions."
    generated_plan = planner.plan(sample_goal)
    print("\n✅ Plan Generated Successfully:")
    print(f"Objective: {generated_plan.objective}\n")
    for task in generated_plan.tasks:
        print(f"Task #{task.id} [{task.agent_type.value.upper()}]: {task.description}")