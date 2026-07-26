from model import Plan
from llm import call_llm
from llm import stream_llm
from agents.base_agent import run_agent

async def planner(user_query: str)-> Plan:
    messages =[
            {
                "role": "system",

                "content": """
                You are a Task Planner Agent.

                Your responsibility is to break a user's request into smaller tasks.

                Available Agents:

                1. news
                   Use for:
                   - latest news
                   - current events
                   - announcements
                   - recent developments

                2. research
                   Use for:
                   - analysis
                   - explanations
                   - comparisons
                   - insights
                   - business impact

                Planning Rules:

                - Create only the tasks that are necessary.
                - Each task should be handled by exactly one agent.
                - Keep task descriptions short and clear.
                - Priorities:
                    1 = Highest
                    5 = Lowest

                Return ONLY valid JSON.

                Example:

                {
                    "tasks":[
                        {
                            "agent":"news",
                            "task":"Find latest AI developments",
                            "priority":1
                        },
                        {
                            "agent":"research",
                            "task":"Analyse the business impact",
                            "priority":2
                        }
                    ]
                }

                Do not return markdown.

                Do not explain your reasoning.

                Return JSON only.
                """
            },
            {
                'role':'user',
                'content': f"""User request:{user_query}
                Create a task plan using the required JSON format."""
            }
        ]
    return await run_agent(messages, output_model=Plan)