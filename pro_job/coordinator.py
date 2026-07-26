import asyncio
from agents.news import news
from agents.resarch import research
from agents.planner import planner
from agents.stream_planner import stream_planner
from parsers.streming_parser import parse_json_stream
from agents.aggregator import aggregator
from model import AgentTask,ResultTask,FinalAnswer



async def coordinator():
    research_queue = asyncio.Queue()
    news_queue = asyncio.Queue()
    result_queue = asyncio.Queue()

    

    user_query = """Find the latest AI developments
    and analyze their impact on business."""

    

    workers = [
        asyncio.create_task(news(news_queue, result_queue)),
        asyncio.create_task(research(research_queue,result_queue))
    ]

    print('planning start.......')

    async for plan in stream_planner(user_query):
        print(plan)

        #---------------
        #running News Agent First
        #---------------


        for task in plan.tasks:
            if task.agent == "news":

                await news_queue.put(task)
        
        await news_queue.join()

        #-----------------
        #collecting NEws result
        #-----------------
        news_results = []

        while not result_queue.empty():
            result = await result_queue.get()
            
            if result.agent == 'news':
                news_results.append(result)
            
        
        print("News completed")
        print(news_results)

        #-------------
        #Sending resutl to research agent
        #-------------

        for task in plan.tasks:
            if task.agent == 'research':
                task.task += f"""
                                Use this news information:

                                {news_results}

                                Analyze the business impact.
                            """
                await research_queue.put(task)
        await research_queue.join()

        #--------------
        #Collecting all result
        #--------------
        results = []

        while not research_queue.empty():
            result.append(
                await research_queue.get()
            )
        results.extend(news_results)

        #-------------
        #Aggreator 
        #-------------
        final_answer = await aggregator(results)

        print('===============Final Answer================')
        print(final_answer)

        break

    await news_queue.put(None)
    await research_queue.put(None)
    await asyncio.gather(*workers)

if __name__ == "__main__":
    asyncio.run(coordinator())

    
