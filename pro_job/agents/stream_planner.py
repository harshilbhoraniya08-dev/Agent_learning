from llm import stream_llm
from parsers.streming_parser import parse_json_stream
from model import Plan

def build_planner_messages(user_query):
    return [
        {

            "role": "system",
            "content": """
            You are a task planner.

            Your ONLY job is to create a JSON task plan.

            Available agents:

            1. news
            - latest news
            - announcements
            - current events

            2. research
            - analysis
            - explanation
            - business impact


            Return ONLY raw JSON.

            Never return:
            - markdown
            - explanations
            - safety messages
            - comments

            The format MUST be:

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
                "role":"user",
                "content":user_query
            }
    ]


async def stream_planner(user_query):
    messages = build_planner_messages(user_query)
    token_stream = stream_llm(messages)

    async for data in parse_json_stream(token_stream):
        try:
            plan = Plan.model_validate(data)
            print('Planner Compeleted')
            yield plan
        except Exception as e:
            print(f"Planner Validation Error: {e}")