import asyncio
from tools.tool_registery import TOOLS
from tools.tool_executor import execute_tool
from llm import call_llm_with_tools

async def run_agent(messages, output_model=None):
    while True:
        responce = await call_llm_with_tools(messages)
        message = responce.choices[0].message
        print("----------------")
        print("ROLE:", message.role)
        print("CONTENT:", message.content)
        print("TOOL CALLS:", message.tool_calls)
        print("----------------")
        messages.append(message)


        if message.tool_calls:
            tool_call = message.tool_calls[0]
            result = await execute_tool(tool_call)
            messages.append(
                {
                    "role":"tool",
                    "tool_call_id":tool_call.id,
                    "content":str(result)
                }
            )
            print('Final Tool Result:')
            print(result)
        else:
            return message.content
