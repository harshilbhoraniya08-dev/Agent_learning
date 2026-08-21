import sys
from orchestration.engine import OrchestratorEngine

def save_markdown_report(report,filename="report.md"):
    """this will save the structured final report"""
    content = f"# {report.title}\n\n"
    content += f"## Excutive summary\n{report.executive_summary}\n\n"
    content += "## key Findings\n"
    for item in report.key_findings:
        content += f"-{item}\n"
    content += "\n## Refrences & Sources Cited\n"
    for src in report.sources:
        content += f"-{src}\n"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n Report saved to: {filename}")

def main():
    default_prompt = "Analyze the latest developments and performance benchmarks of open-weight small language models (SLMs)."

    print("--- 🤖 Multi-Agent Research Operating System ---")
    user_query = input(f"\nEnter research objective (Press Enter for default):\n> ").strip()

    if not user_query:
        user_query = default_prompt

    engine = OrchestratorEngine()
    report = engine.run(user_query)

    print("\n" + "=" * 60)
    print("📋 FINAL EXECUTIVE DELIVERABLE")
    print("=" * 60)
    print(f"\nTitle: {report.title}")
    print(f"\nExecutive Summary:\n{report.executive_summary}")
    print("\nKey Findings:")
    for item in report.key_findings:
        print(f"  • {item}")
    print(f"\nSources:\n  {', '.join(report.sources) if report.sources else 'None cited'}")
    print("=" * 60)

    save_markdown_report(report)


if __name__ == "__main__":
    main()