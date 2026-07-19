import asyncio
from agents.news import news
from agents.resarch import research
from agents.planner import planner
from agents.stream_planner import stream_planner
from parsers.streming_parser import parse_json_stream
from model import AgentTask,ResultTask

async def coordinator():
    research_queue = asyncio.Queue()
    news_queue = asyncio.Queue()
    result_queue = asyncio.Queue()

    user_query = """Find the latest AI developments
    and analyze their impact on business."""

    print('planning start.......')
    async for plan in stream_planner(user_query):
        print(plan)


        for task in plan.tasks:
        
            if task.agent == 'news':
                await news_queue.put(task)
            elif task.agent == 'research':
                await research_queue.put(task)

        asyncio.create_task(news(news_queue, result_queue))
        asyncio.create_task(research(research_queue,result_queue))

        await research_queue.join()
        await news_queue.join()

        await asyncio.gather(
            research_queue.join(),
            news_queue.join()
        )

        while not result_queue.empty():
            result = await result_queue.get()
            print(result)
    
asyncio.run(coordinator())

    
