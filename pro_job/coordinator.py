import asyncio
from agents.news import news
from agents.resarch import research
from agents.planner import planner
from agents.stream_planner import stream_planner
from parsers.streming_parser import parse_json_stream
from agents.aggregator import aggregator
from model import AgentTask,ResultTask,FinalAnswer


AGENTS = {
    'news':news,
    'research':research
}


async def coordinator():

    #-------------------
    # queue
    #-------------------
    queues = {
        'news': asyncio.Queue(),
        'research': asyncio.Queue()
        }
    
    result_queue = asyncio.Queue()

    #-------------
    # Working Start
    #-------------

    workers = []

    for agent_name, worker in AGENTS.items():
        workers.append(
            asyncio.create_task(
                worker(
                    queues[agent_name],result_queue 
                )
            )
        )

    

    user_query = """Find the latest AI developments
    and analyze their impact on business."""

    

    

    print('planning start.......')

    async for plan in stream_planner(user_query):
        print(plan)
        break

        #---------------
        #DEpendencies
        #---------------

    pending = list(plan.tasks)

    completed = {}

    while pending:
        progress = False

        for task in pending[:]:

            if all(dep in completed for dep in task.depends_on):
                print(f"\nRunning: {task.id}")

                if task.depends_on:
                    context = []
                    for dep in task.depends_on:
                        context.append(
                            completed[dep].result.model_dump_json(indent=2))
                    task.task += f"""Previous Task Results:
                    {chr(10).join(context)}
                    Use these results while answering."""

                queue = queues[task.agent]
                await queue.put(task)
                await queue.join()

                result = await result_queue.get()
                completed[task.id] = result
                pending.remove(task)
                progress = True
        if not progress:
            raise RuntimeError(
                'circular dependcy detected'
            )
        
    final_answer = await aggregator(list(completed.values()))
    print("\n========================")
    print(final_answer)
    print("========================")

     # ---------------------------------------
    # Stop workers
    # ---------------------------------------

    for queue in queues.values():
        await queue.put(None)

    await asyncio.gather(*workers)

if __name__ == '__main__':
    asyncio.run(coordinator())
        