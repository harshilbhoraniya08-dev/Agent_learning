import json
import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from models import AgentOutput, Task
from config import settings
from llm import llm_client
from tools.registry import tool_registry

NEWS_SYSTEM_PROMPT = """
You are a specialized Market & News Intelligence Agent.
Your goal is to gather recent news, media coverage, industry sentiment, and executive reactions for an assigned task.

You operate in a ReAct loop:
1. Reason about what recent events, sentiments, or announcements are relevant.
2. If you need live information, call a tool by outputting:
   Action: tool_name
   Action Input: {{"param_name": "value"}}
3. When you have gathered sufficient news data, conclude with:
   Final Findings: <concise summary of news, sentiment, timeline, and stakeholder reactions>

Available Tools:
__TOOLS_DESCRIPTION__
"""


class NewsAgent:
    #worker working to gather news and deep market analysis

    def __init__(self):
        self.llm = llm_client
        self.max_loops = settings.MAX_LOOPS

    def execute_task(self, task:Task) ->AgentOutput:
        #Runs the react loop focusing on market sentiments

        tools_schemas = tool_registry.get_schemas()
        formatted_prompt = NEWS_SYSTEM_PROMPT.format(
            "__TOOLS_DESCRIPTION__", json.dumps(tools_schemas, indent=2)
        )

        conversation_history = f"Task Description: {task.description}\n"
        sourced_collected = []

        print(f"\n [NewsAgent] Starting Task #{task.id}: {task.description}")

        # react loop reasoning
        for loop_idx in range(self.max_loops):
            print(f"   Iteration {loop_idx + 1}/{self.max_loops}...")

            response = self.llm.generate_text(
                system_prompt=formatted_prompt,
                user_prompt=conversation_history,
                use_fast_model=True,
                temperature=0.2
            )

            #checking the agent is finished or not
            if "Final Findings" in response:
                finding_text = response.split("Final Findings")[-1].strip()
                print("Task done")
                return AgentOutput(
                    agent_name="NewsAgent",
                    task_id=task.id,
                    findings=finding_text,
                    sources=sourced_collected
                )

            #parse action and action input
            action_match = re.search(r"Action:\s*(\w+)", response)
            input_match = re.search(r"Action Input:\s*(\{.*\}|[^\n]+)", response)

            if action_match and input_match:
                tool_name = action_match.group(1).strip()
                raw_args = input_match.group(1).strip()

                try:
                    kwargs = json.loads(raw_args) if raw_args.startswith("{") else {"query": raw_args}
                except json.JSONDecodeError:
                    kwargs = {"query": raw_args}

                print(f"   Executing Tool: {tool_name}({kwargs})")
                observation = tool_registry.execute(tool_name, **kwargs)
                sourced_collected.append(f"{tool_name}: {kwargs.get('query', 'direct_call')}")

                conversation_history += (
                    f"\nThought/Action:\n{response}\n"
                    f"Observation: {observation}\n"
                )
            else:
                print("General sentiment findings produced.")
                return AgentOutput(
                    agent_name="NewsAgent",
                    task_id=task.id,
                    findings=response.strip(),
                    sources=sourced_collected
                )
        print(" Max loops reached")
        return AgentOutput(
            agent_name="NewsAgent",
            task_id=task.id,
            findings=f"Partial news summary: {conversation_history[-500:]}",
            sources=sourced_collected

        )

if __name__ == "__main__":
    from models import AgentType

    test_task = Task(
        id=2,
        agent_type=AgentType.NEWS,
        description="Gather industry reactions and startup sentiment regarding the new AI safety regulations.",
    )

    agent = NewsAgent()
    output = agent.execute_task(test_task)

    print("\n--- Final Agent Output ---")
    print(f"Task ID: {output.task_id}")
    print(f"Agent: {output.agent_name}")
    print(f"Findings:\n{output.findings}")
    print(f"Sources: {output.sources}")