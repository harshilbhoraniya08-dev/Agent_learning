import asyncio
from model import AgentTask, ResultTask, SearchInput, ResearchAnalysis
from tools.search_tools import search_tool
from llm import call_llm
from agents.base_agent import run_agent

async def research(queue, result_queue):
    while True:
        task_data = await queue.get()
        task = AgentTask.model_validate(task_data)
        if task.agent=='research':
            print('research task start')
            messages = [
                {
                    "role":"system",
                    "content":"""
                    You are a research analyst.

                    You can use available tools whenever needed.

                    Your job is:
                    - Research the topic
                    - Analyze deeply
                    - Explain findings
                    - Compare information
                    - Give insights

                    Use tools whenever they are helpful before answering."""
                },
                {
                    "role":"user",
                    "content":task.task
                }
            ]

            answer = await run_agent(messages, output_model=ResearchAnalysis)

            result = ResultTask(agent=task.agent,result=answer)
            await result_queue.put(result)
        queue.task_done()