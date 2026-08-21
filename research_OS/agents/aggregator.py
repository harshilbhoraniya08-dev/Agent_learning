import sys
from pathlib import Path
from typing import List

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from models import FinalReport, AgentOutput
from llm import llm_client

AGGREGATOR_SYSTEM_PROMPT = """
You are the Executive Synthesis Agent in an enterprise Multi-Agent Research Operating System.
Your job is to take raw research outputs from multiple specialized worker agents and compile them into a unified, high-impact executive report.

Requirements:
- Structure the findings cleanly.
- Create an executive summary suitable for leadership.
- Compile a clear list of key takeaways.
- Deduplicate and list all reference sources.
"""


class AggregatorAgent:
    def __init__(self):
        self.llm = llm_client

    def aggregate(self, objective:str, outputs:List[AgentOutput]) -> FinalReport:
        """Combining the multiple output from multi agent to get final report"""

        compiled_findings = ""
        for out in outputs:
            compiled_findings += f"\n--- Output from {out.agent_name} (Task #{out.task_id}) ---\n"
            compiled_findings += f"Findings:\n{out.findings}\n"
            if out.sources:
                compiled_findings += f"Sources: {', '.join(out.sources)}\n"

        user_prompt = (
            f"Original Objective: {objective}\n\n"
            f"Worker Agent Findings: \n{compiled_findings}\n\n"
            f"Complie these findings into the structured FinalReport schema. "
        )

        print("\n [AggregatorAgent] Syntesis final report...")

        report: FinalReport = self.llm.generate_structured(
            system_prompt=AGGREGATOR_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            use_fast_model=False,
            response_model=FinalReport,
        )

        return report

if __name__ == "__main__":
    sample_outputs = [
        AgentOutput(
            agent_name="ResearchAgent",
            task_id=1,
            findings="The EU AI Act introduces strict transparency rules for general-purpose AI (GPAI) models, exempting open-source models unless they pose systemic risk.",
            sources=["search_web: EU AI Act technical guidelines"],
        ),
        AgentOutput(
            agent_name="NewsAgent",
            task_id=2,
            findings="Open-source developers and startup founders expressed concern over potential compliance costs and ambiguity in systemic risk definitions.",
            sources=["search_web: open source AI safety sentiment"],
        ),
    ]

    aggregator = AggregatorAgent()
    final_report = aggregator.aggregate(
        objective="Analyze the impact of the EU AI Act on open-source AI developers.",
        outputs=sample_outputs,
    )

    print("\n✅ Final Report Generated Successfully:")
    print(f"Title: {final_report.title}")
    print(f"\nExecutive Summary:\n{final_report.executive_summary}")
    print(f"\nKey Findings:")
    for finding in final_report.key_findings:
        print(f" - {finding}")
    print(f"\nSources: {final_report.sources}")