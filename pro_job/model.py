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

class Plan(BaseModel):
    tasks: List[AgentTask]

#-------------
# Agent Result
#-------------
    
class ResultTask(BaseModel):
    agent:str
    result:Any

#-------------
# Analysis Outputs
#-------------


class NewsAnalysis(BaseModel):
    title: str
    summary: str
    key_points: list[str]
    confidence: float = Field(
         ge=0,
         le=1
    )

class ResearchAnalysis(BaseModel):
    title: str
    summary: str
    key_points: list[str]
    confidence: float = Field(
         ge=0,
         le=1
    )

#---------------
# Input/Outpu (Tools)
#---------------

class SearchInput(BaseModel):
    query:str
    max_result:int = 5

class SearchResult(BaseModel):
        articles: list[str]

#----------------
# Final Answer
#----------------
        
class FinalAnswer(BaseModel):
    title: str
    summary: str

    key_insights: list[str] = Field(
        default_factory=list
    )

    key_points: list[str] = Field(
        default_factory=list
    )

    recommendations: list[str] = Field(
        default_factory=list
    )

    confidence: float = 0.0