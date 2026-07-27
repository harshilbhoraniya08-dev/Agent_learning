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

                        Your job:
                        - Find latest news
                        - Analyze important developments
                        - Summarize impact
                        - Extract key points


                        IMPORTANT:

                        Your final response MUST be valid JSON.

                        Return ONLY:

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
                        - No markdown
                        - No explanations
                        - No ```json
                        - JSON only.
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

        