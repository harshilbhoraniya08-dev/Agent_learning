import asyncio
from model import AgentTask, ResultTask, SearchInput, SearchResult, NewsAnalysis
from tools.search_tools import search_tool
from llm import call_llm

async def news(queue, result_queue):
    while True:
        task_data = await queue.get()
        task = AgentTask.model_validate(task_data)
        if task.agent == 'news':
            print('News seach start')
            search = SearchInput(
                query=task.task,
                max_result=5
            )
            articles = await search_tool(search)
            answer = await call_llm(
                [
                    {
                    'role':'system',
                    'content':"""
                    You are a news analyst agent.
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
                    'content':f"""Task:{task.task}   News data: {articles}"""
                        
                    }
                ], NewsAnalysis
            )
            result = ResultTask(
                agent=task.agent, result=answer
            )
            await result_queue.put(result)
        queue.task_done()

        