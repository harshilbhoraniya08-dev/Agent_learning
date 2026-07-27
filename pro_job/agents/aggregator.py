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
            You are the final intelligence analyst.

            You receive reports from multiple AI agents.

            Your job:
            1. Combine ALL reports.
            2. Do not copy one report.
            3. Create a higher-level conclusion.
            4. Extract business insights.
            5. Provide recommendations.

            Return ONLY JSON.

            Format:

            {
            "title":"",
            "summary":"",
            "key_insights":[],
            "recommendations":[],
            "confidence":0.0
            }

            Important:
            - Use both news and research reports.
            - Focus on business implications."""
        },
        {
            'role':'user',
            'content':json.dumps(results_json, indent=2)
        }
    ]

    answer = await run_agent(messages, output_model=FinalAnswer)
    return answer