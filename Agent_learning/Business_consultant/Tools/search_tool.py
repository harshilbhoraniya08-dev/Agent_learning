import logging
from typing import Dict,Any,List
from duckduckgo_search import DDGS
from core.model import SearchInput,SearchResult,Article
from Tools.tool_registery import register_tool 

logger = logging.getLogger(__name__)

async def web_search(query:str, max_result:int = 5) -> Dict[str, Any]:
    logger.info(f"[Tool Execution] web_search: query='{query}' limit={max_result}")

    try:
        search_input = SearchInput(query=query, max_result=max_result)
        articles: List[Article] = []

        with DDGS() as ddgs:
            raw_results = list(ddgs.text(search_input.query, max_results=search_input.max_result))

            for item in raw_results:
                article = Article(title=item.get('title', 'Untitled'), url=item.get('href', ''), snippet=item.get('body', ''))
                articles.append(article) 

        search_result = SearchResult(articles=articles)
        return search_result.model_dump()
    except Exception as e:
        logger.error(f"[Tool Error] web_serach execution failed: {str(e)}")
        return SearchResult(articles=[]).model_dump()
    

#======================================================
# Schema Declatration and Auto Registration
#======================================================
    
SEARCH_TOOL_SCHEMA = {
    "type": "function",
    "function":{
        "name": "web_search",
        "description":"Search the web for recent news, up-to-date facts and current documentation.",
        "parameters":{
            "type":"object",
            "properties":{
                "query":{
                    "type":"string",
                    "description":"The exect web serch query"
                },
                "max_result":{
                    "type":"integer",
                    "description":"Maximum number of articles to return.",
                    "default":5
                }
            },
            "required":["query"]
        }
    }
}


def register_search_tool():
    register_tool(schema=SEARCH_TOOL_SCHEMA, function=web_search)

register_search_tool()