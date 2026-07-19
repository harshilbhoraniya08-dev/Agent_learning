from pydantic import BaseModel, Field
from typing import Any, Optional,List

class AgentTask(BaseModel):
    agent:str
    task:str
    priority:int=Field(
        default=3,
        ge=1,
        le=5
    )

class ResultTask(BaseModel):
    agent:str
    result:Any

class NewsAnalysis(BaseModel):
    title: str
    summary: str
    key_points: list[str]
    confidence: float

class ResearchAnalysis(BaseModel):
    title: str
    summary: str
    key_points: list[str]
    confidence: float

class SearchInput(BaseModel):
    query:str
    max_result:int

class SearchResult(BaseModel):
        articles: list[str]

class Plan(BaseModel):
    tasks: List[AgentTask]