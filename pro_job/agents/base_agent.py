import json

from tools.tool_executor import execute_tool
from llm import call_llm_with_tools
from utils.json_parser import parse_json


async def run_agent(messages, output_model=None):

    while True:

        response = await call_llm_with_tools(messages)

        message = response.choices[0].message

        print("----------------")
        print("ROLE:", message.role)
        print("CONTENT:", message.content)
        print("TOOL CALLS:", message.tool_calls)
        print("----------------")


        # If LLM wants to use tools
        if message.tool_calls:

            messages.append(message)


            for tool_call in message.tool_calls:

                result = await execute_tool(tool_call)

                print("Final Tool Result:")
                print(result)


                if hasattr(result, "model_dump"):
                    tool_content = json.dumps(result.model_dump())

                else:
                    tool_content = json.dumps(result)


                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_content,
                    }
                )


            # IMPORTANT CHANGE
            # Tell model to return structured output after tools

            if output_model is not None:

                messages.append(
                    {
                        "role":"system",
                        "content": f"""
                        Using the tool results above, now provide the final answer.

                        Return ONLY valid JSON.

                        Schema:

                        {json.dumps(output_model.model_json_schema(), indent=2)}
                        """
                    }
                )


            continue



        # Final response without tools

        if output_model is not None:

            try:

                data = parse_json(message.content)

                return output_model.model_validate(data)


            except json.JSONDecodeError as e:

                raise ValueError(
                    f"""
                    Model returned invalid JSON.

                    Expected schema:
                    {output_model.model_json_schema()}

                    Received:
                    {message.content}
                    """
                ) from e


        return message.content