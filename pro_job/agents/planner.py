from model import Plan
from llm import call_llm
from llm import stream_llm

async def planner(user_query):
    plan = await call_llm(
        [
            {
                'role':'system',
                'content':'''You are a task planner agent.
                Your job is to decide which agent should handle a user request.
                Available agents:
                1. news:
                Use for latest news, events, announcements.
                2. research:
                Use for analysis, explanation, comparison.
                Return ONLY JSON.
                You MUST follow this exact structure:
                {
                    "tasks": [
                        {
                            "agent": "news",
                            "task": "Find latest AI developments",
                            "priority": 1
                        },
                        {
                            "agent": "research",
                            "task": "Analyze business impact",
                            "priority": 2
                        }
                        ]
                        }
                        Rules:
                        - Do not return "plan"
                        - Do not return only agent names
                        - Every task must contain agent, task, priority'''
            },
            {
                'role':'user',
                'content': f"""User request:{user_query}
                Create a task plan using the required JSON format."""
            }
        ], Plan
    )

    return plan


       