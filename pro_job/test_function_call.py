import asyncio

from agents.base_agent import run_agent


async def main():

    messages = [
        {
            "role":"user",
            "content":"Find the latest AI tool"
        }
    ]

    answer = await run_agent(messages)

    print("Final Answer:")
    print(answer)


asyncio.run(main())