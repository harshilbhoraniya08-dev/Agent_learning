from model import FinalAnswer
from agents.base_agent import run_agent
import json

async def aggregator(results):

    results_json = [
        result.model_dump()
        for result in results
    ]

    messages = [
        {
            'role':'system',
            'content':"""
            You are a senior AI analyst.

            Your job is to combine multiple agent reports into one final answer.

            You MUST return ONLY valid JSON.

            The JSON must exactly follow this structure:

            {
                "title": "string",
                "summary": "string",
                "key_insights": [
                    "string"
                ],
                "recommendations": [
                    "string"
                ],
                "confidence": 0.0
            }

            Rules:
            - Do not use markdown.
            - Do not add explanations.
            - Do not change field names.
            - Always include all fields."""
        },
        {
            'role':'user',
            'content':json.dumps(results_json, indent=2)
        }
    ]

    answer = await run_agent(messages, output_model=FinalAnswer)
    return answer