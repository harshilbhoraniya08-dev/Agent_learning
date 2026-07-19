import asyncio
from model import AgentTask, ResultTask, SearchInput, ResearchAnalysis
from tools.search_tools import search_tool
from llm import call_llm

async def research(queue, result_queue):
    while True:
        task_data = await queue.get()
        task = AgentTask.model_validate(task_data)
        if task.agent=='research':
            print('research task start')
            search = SearchInput(
                query=task.task,
                max_result=5
            )
            data = await search_tool(search)
            answer = await call_llm(
                [
                    {
                    'role':'system',
                    'content':"""
                    You are a research analyst agent.
                    Analyze the provided news.

                    Return ONLY JSON with this exact structure:
                    {
                        "title": "string",
                        "summary": "string",
                        "key_points": [
                            "point 1",
                            "point 2"],
                        "confidence": 0.95
                    }
                    Rules:
                    - title must be a string
                    - summary must explain the news
                    - key_points must contain important facts
                    - confidence must be a number between 0 and 1
                    """
                    },

                    {
                        'role':'user',
                        'content':f"""Task : {task.task}   New data : {data}"""
                    }
                ], ResearchAnalysis
            )
            result = ResultTask(agent=task.agent,result=answer)
            await result_queue.put(result)
        queue.task_done()