import asyncio
import streamlit as st
import streamlit.components.v1 as components
from database.database import init_db
from Agents.react import ReActAgent
from orchestration.planner import Planner
from orchestration.dependency_engine import DependencyEngine
from orchestration.coordinator import Coordinator
from governance.memory_manager import MemoryManager
from governance.supervisor import Supervisor
from database.database import get_all_task
import pandas as pd

init_db()

# Streamlit page config must be set before any other Streamlit calls
st.set_page_config(page_title="Multi-Agent Operations Studio", page_icon="✨", layout="wide")

st.title('Agent monitor Activity')

if st.button("Refresh Task Monitor"):
    tasks = get_all_task()

    data = [
        {"id": t.id, "agent": t.agent, "task": t.task, "status": t.status.value, "created_at": t.created_at}
        for t in tasks
    ]

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
# ---------------------------------------------------------
# 1. PAGE CONFIG & CUSTOM MODERN CSS
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Background & Global Reset */
    .stApp {
        background-color: #f8fafc;
        color: #0f172a;
    }
    
    /* Sleek Rounded Cards */
    .custom-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    .custom-card:hover {
        border-color: #cbd5e1;
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.08);
    }
    
    /* Glowing Header Gradient Card */
    .hero-card {
        background: linear-gradient(135deg, #fff5f5 0%, #fef2f2 50%, #faf5ff 100%);
        border: 1.5px solid #fbcfe8;
        border-radius: 20px;
        padding: 20px;
    }
    
    /* Dark Action Button */
    .stButton>button {
        background-color: #0f172a !important;
        color: #ffffff !important;
        border-radius: 12px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        border: none !important;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #1e293b !important;
    }
    
    /* Agent Micro Cards */
    .agent-pill {
        background: #f1f5f9;
        border-radius: 16px;
        padding: 16px;
        text-align: center;
        border: 1px solid #e2e8f0;
    }
    .agent-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 12px auto;
        font-size: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. HEADER & CONTROL PANEL
# ---------------------------------------------------------
st.title("✨ Multi-Agent System Studio")
st.markdown("Orchestrate autonomous agent execution and monitor multi-role dataflow in real time.")

col_left, col_right = st.columns([1, 1.2])

with col_left:
    # Card 1: Operation Objective Input
    st.markdown("""
    <div class="hero-card">
        <h4 style="margin:0 0 8px 0; color:#0f172a;">🎯 Active Mission Objective</h4>
        <p style="color:#64748b; font-size:14px; margin-bottom:0;">Decompose objectives into agent task graphs with automatic dependency resolution.</p>
    </div>
    """, unsafe_allow_html=True)
    
    objective = st.text_area(
        "Enter System Prompt / Objective",
        value="Compare REST vs GraphQL APIs for mobile app backends and recommend the best choice.",
        height=100
    )
    
    run_btn = st.button("🚀 Launch Execution Pipeline")

with col_right:
    # Card 2: Main System Status Visualizer
    st.markdown("""
    <div class="custom-card" style="text-align: center; padding: 36px 24px;">
        <div style="font-size: 40px; margin-bottom: 12px;">🤖</div>
        <h3 style="margin: 0 0 8px 0;">Autonomous AI Mesh Engine</h3>
        <p style="color: #64748b; font-size: 14px; max-width: 400px; margin: 0 auto 20px auto;">
            Powered by 5-Pillar Architecture: Planning, ReAct Reasoning Loops, Parallel Coordination, and Supervisor Audit.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------
# 3. AGENT ROSTER CARDS (THE 3 WORKERS)
# ---------------------------------------------------------
st.subheader("👥 Active Agent Roster")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="custom-card" style="text-align:center;">
        <div class="agent-icon" style="background:#e0f2fe; color:#0284c7;">🔍</div>
        <h4 style="margin:0;">ResearchAgent</h4>
        <p style="color:#64748b; font-size:12px; margin-top:4px;">Pillar 3: Brain + Tools</p>
        <span style="background:#dcfce7; color:#15803d; font-size:11px; padding:4px 10px; border-radius:12px; font-weight:600;">Tool: Web Search</span>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="custom-card" style="text-align:center;">
        <div class="agent-icon" style="background:#fef3c7; color:#d97706;">📊</div>
        <h4 style="margin:0;">AnalystAgent</h4>
        <p style="color:#64748b; font-size:12px; margin-top:4px;">Pillar 3: ReAct Brain</p>
        <span style="background:#f1f5f9; color:#475569; font-size:11px; padding:4px 10px; border-radius:12px; font-weight:600;">Reasoning Only</span>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="custom-card" style="text-align:center;">
        <div class="agent-icon" style="background:#f3e8ff; color:#9333ea;">✍️</div>
        <h4 style="margin:0;">WriterAgent</h4>
        <p style="color:#64748b; font-size:12px; margin-top:4px;">Pillar 3: Synthesizer</p>
        <span style="background:#f1f5f9; color:#475569; font-size:11px; padding:4px 10px; border-radius:12px; font-weight:600;">Documentation</span>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. EXECUTION CONTROLLER & SYNTHESIS OUTPUT
# ---------------------------------------------------------
async def execute_system():
    # Setup Agents
    researcher = ReActAgent("ResearchAgent", "Researcher", "Search for technical facts.", ["web_search"])
    analyst = ReActAgent("AnalystAgent", "Analyst", "Analyze trade-offs and options.", [])
    writer = ReActAgent("WriterAgent", "Writer", "Draft report.", [])
    
    agent_pool = {"Researcher": researcher, "Analyst": analyst, "Writer": writer}
    planner = Planner([
        {"role": "Researcher", "description": "Searches web facts."},
        {"role": "Analyst", "description": "Compares data."},
        {"role": "Writer", "description": "Drafts report."}
    ])
    memory = MemoryManager()
    supervisor = Supervisor(memory_manager=memory)

    st.markdown("### ⚙️ Execution Pipeline & Dataflow")

    with st.status("Running Multi-Agent System Pipeline...", expanded=True) as status:
        st.write("📌 **Pillar 4 (Planner):** Decomposing objective into task DAG...")
        plan = await planner.create_plan(objective)
        
        st.write(f"⚡ **Pillar 4 (Dependency Engine):** Generated {len(plan.tasks)} parallel execution tasks.")
        
        st.write("🔄 **Pillar 4 (Coordinator):** Dispatching tasks to ReAct agent workers...")
        coordinator = Coordinator(agent_pool=dict(agent_pool), default_agent=researcher)
        results = await coordinator.run_plan(plan)
        
        st.write("👑 **Pillar 5 (Supervisor):** Auditing and synthesizing final report...")
        final_output = await supervisor.evaluate_and_synthesize(objective, results)
        
        status.update(label="Execution Completed Successfully!", state="complete")

    st.markdown("### 📄 Final Synthesized Deliverable")
    st.markdown(f"""
    <div class="custom-card">
        {final_output}
    </div>
    """, unsafe_allow_html=True)

if run_btn:
    asyncio.run(execute_system())