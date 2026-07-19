from llm import stream_llm
from parsers.streming_parser import parse_json_stream
from model import Plan

async def stream_planner(user_query):

    messages = [
        {
            "role": "system",
            "content": """
                You are a task planner agent.

                Your job is to decide which agent should handle the user's request.

                Available agents:
                1. news
                            2. research

            Return ONLY valid JSON.

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
            """
        },
        {
            "role": "user",
            "content": user_query
        }
    ]

    token_stream = stream_llm(messages)

    async for data in parse_json_stream(token_stream):
        plan = Plan.model_validate(data)
        yield plan