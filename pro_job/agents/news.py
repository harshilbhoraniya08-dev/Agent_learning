import asyncio
from model import AgentTask, ResultTask, SearchInput, SearchResult, NewsAnalysis
from tools.search_tools import search_tool
from llm import call_llm
from agents.base_agent import run_agent

async def news(queue, result_queue):
    while True:
        task_data = await queue.get()
        if task_data is None:
            queue.task_done()
            print("News worker stopped.")
            break
        try:
            task = AgentTask.model_validate(task_data)
            if task.agent == 'news':
                print('News seach start')
                messages = [
                    {
                        "role":"system",
                        "content":"""You are a news analyst.

                        You can use available tools whenever needed.

                        Your job is:
                        - Find the latest news
                        - Analyze the news
                        - Summarize important information
                        - Give clear key points

                        Use tools whenever they are helpful before answering.
                        """
                    }, 
                    {
                        "role":"user",
                        "content":task.task
                    }
                ]
                answer = await run_agent(messages,output_model=NewsAnalysis)
                await result_queue.put(
                    ResultTask(agent='news', result=answer)
                )
        except Exception as e:
            print(f"News Agent Error: {e}")
        finally:
            queue.task_done()

        