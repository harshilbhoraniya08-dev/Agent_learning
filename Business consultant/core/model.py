from pydantic import BaseModel, Field
from typing import Any, Optional, List


# ======================
# PLANNING
# ======================

class AgentTask(BaseModel):
    id: str
    
    task: str
    assigned_agent:str

    priority: int = Field(
        default=3,
        ge=1,
        le=5
    )

    depends_on: List[str] = Field(
        default_factory=list
    )

    status: str = "pending"



class Plan(BaseModel):
    objective: str
    tasks: List[AgentTask]



# ======================
# RESULTS
# ======================

class ResultTask(BaseModel):
    task_id: str
    agent: str
    result: Any
    error: Optional[str] = None



# ======================
# SEARCH
# ======================

class SearchInput(BaseModel):
    query: str
    max_result: int = 5



class Article(BaseModel):
    title: str
    url: str
    snippet: str



class SearchResult(BaseModel):
    articles: List[Article]



# ======================
# AGENT OUTPUTS
# ======================


class NewsAnalysis(BaseModel):
    title: str
    summary: str
    key_points: List[str]
    confidence: float



class ResearchAnalysis(BaseModel):
    title: str
    summary: str
    key_insights: List[str]
    recommendations: List[str]
    confidence: float



# ======================
# REACT LOOP
# ======================


class Thought(BaseModel):
    reasoning: str



class Action(BaseModel):
    tool_name: str
    tool_input: dict



class Observation(BaseModel):
    result: Any



# ======================
# MEMORY
# ======================


class MemoryItem(BaseModel):
    id: str
    content: str
    source: str
    score: float



# ======================
# REFLECTION
# ======================


class Reflection(BaseModel):
    success: bool
    feedback: str
    improvements: List[str]