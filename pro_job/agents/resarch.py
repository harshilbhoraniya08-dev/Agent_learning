import asyncio
from model import AgentTask, ResultTask, SearchInput, ResearchAnalysis
from tools.search_tools import search_tool
from llm import call_llm
from agents.base_agent import run_agent

async def research(queue, result_queue):
    while True:
        task_data = await queue.get()
        if task_data is None:
            queue.task_done()
            print('research agent stopped')
            break

        try:
            task = AgentTask.model_validate(task_data)

            if task.agent!='research':
                continue
            print('research task start')
            messages = [
                    {
                        "role": "system",
                        "content": """
                        You are an expert Research Agent.

                        You may use available tools whenever needed.

                        Your responsibilities:

                        - Research the topic.
                        - Analyse it deeply.
                        - Compare different viewpoints.
                        - Explain important findings.
                        - Provide business and technical insights.

                        IMPORTANT:

                        Your FINAL answer MUST be valid JSON.

                        Return ONLY this format:

                        {
                            "title":"string",
                            "summary":"string",
                            "key_points":[
                                "point 1",
                                "point 2"
                            ],
                            "confidence":0.95
                        }

                        Rules:

                        - No markdown.
                        - No explanations.
                        - No extra text.
                        - Return JSON only.
                        """
                    },
                    {
                        "role":"user",
                        "content":task.task
                    }
                ]

            answer = await run_agent(messages, output_model=ResearchAnalysis)

            result = ResultTask(agent=task.agent,result=answer)
            await result_queue.put(result)
        except Exception as e:
            print(f'Research agent Error: {e}')
        finally:
            queue.task_done()