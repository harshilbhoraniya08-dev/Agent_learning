import json
import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from models import AgentOutput,Task
from config import settings
from llm import llm_client
from tools.registry import tool_registry


RESEARCH_SYSTEM_REPORT = """
You are an expert Technical Research Agent.
Your goal is to gather detailed, factual information to complete an assigned research task.

You operate in a ReAct loop:
1. Reason about what information you need.
2. If you need data, call a tool by outputting:
   Action: tool_name
   Action Input: {{"param_name": "value"}}
3. When you have gathered sufficient information, conclude with:
   Final Findings: <comprehensive summary of facts and citations>

Available Tools:
{tools_description}
"""


class ResearchAgent:

    def __init__(self):
        self.llm = llm_client
        self.max_loops = settings.MAX_LOOPS

    def execute_task(self, task: Task) -> AgentOutput:
        #run the react loop schemas into a system prompt
        tool_schemas = tool_registry.get_schemas()
        formatted_prompt =  RESEARCH_SYSTEM_REPORT.format(
            tools_description=json.dumps(tool_schemas, indent=2)
        )

        conversation_history = f"Task Description: {task.description}\n"
        sourced_collected = []

        print(f"\n [ResearchAgent] strating Task #{task.id}: {task.description}")

        for loop_idx in range(self.max_loops):
            print(f"iteration  {loop_idx + 1}/{self.max_loops}....")

            response = self.llm.generate_text(
                system_prompt=formatted_prompt,
                user_prompt=conversation_history,
                use_fast_model=True,
                temperature=0.1
            )

            # Check if the agent is ready with final findings
            if "Final Findings: "in response:
                finding_text = response.split("Final Findings: ")[-1].strip()
                print("Task completed successfully")
                return AgentOutput(
                    agent_name="ResearchAgent",
                    task_id=task.id,
                    findings=finding_text,
                    sources=sourced_collected
                )
            
            #Parse tool execution requests
            action_match = re.search(r"Action:\s*(\w+)", response)
            input_match = re.search(r"Action Input:\s*(\{.*\}|[^\n]+)", response)

            if action_match and input_match:
                tool_name = action_match.group(1).strip()
                raw_args = input_match.group(1).strip()

                try:
                    kwargs = json.loads(raw_args) if raw_args.startswith("{") else {"query": raw_args}
                except:
                    kwargs= {"query": raw_args}

                print(f"   Executing Tool: {tool_name}({kwargs})")

                #running tool safely in tool_registry

                observation = tool_registry.execute(tool_name, **kwargs)
                sourced_collected.append(f"{tool_name}:{kwargs.get('query', 'direct_call')}")

                # update context window for next reasoning loop

                conversation_history += (
                    f"\nThought/Action:\n{response}\n"
                    f"Observation: {observation}\n"
                )
            else:
                #if model gives only raw text without specific formatting
                print("General findings produced")
                return AgentOutput(
                    agent_name="ResearchAgent",
                    task_id = task.id,
                    findings=response.strip(),
                    sources=sourced_collected,
                )
        print(" Max iternation reached.")
        return AgentOutput(
            agent_name="ResearchAgent",
            task_id = task.id,
            findings=f"incomplete findings after max_loops. context:{conversation_history[-500:]}",
            sources=sourced_collected
        )
    
if __name__ == "__main__":
    from models import AgentType

    test_task = Task(
        id=1,
        agent_type=AgentType.RESEARCH,
        description="Extract key compliance requirements for open-source foundation models under the EU AI Act."
    )

    agent = ResearchAgent()
    output = agent.execute_task(test_task)

    print("\n--- Final Agent Output ---")
    print(f"Task ID: {output.task_id}")
    print(f"Agent: {output.agent_name}")
    print(f"Findings:\n{output.findings}")
    print(f"Sources: {output.sources}")