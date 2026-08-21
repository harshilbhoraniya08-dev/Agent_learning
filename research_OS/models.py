# models.py
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class AgentType(str, Enum):
    RESEARCH = "research"
    NEWS = "news"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Task(BaseModel):
    id: int = Field(description="Unique Task ID, starting at 1")
    agent_type: AgentType = Field(description="Target agent role for execution")
    description: str = Field(description="Exact instruction for what to research or extract")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current execution state")
    result: Optional[str] = Field(default=None, description="Raw output generated upon completion")
    error: Optional[str] = Field(default=None, description="Captured exception trace if failed")


class Plan(BaseModel):
    objective: str = Field(description="Original user query or goal")
    tasks: List[Task] = Field(description="Ordered sequence of sub-tasks to execute")


class AgentOutput(BaseModel):
    agent_name: str = Field(description="Name of reporting worker")
    task_id: int = Field(description="Task ID this output resolves")
    findings: str = Field(description="Synthesized facts and data points")
    sources: List[str] = Field(default_factory=list, description="Verified references or URLs")


class FinalReport(BaseModel):
    title: str = Field(description="Concise report title")
    executive_summary: str = Field(description="High-level synthesis for stakeholders")
    key_findings: List[str] = Field(description="Deep breakdown organized by topic")
    sources: List[str] = Field(default_factory=list, description="Deduplicated list of all references")