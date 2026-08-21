from tools.registry import tool_registry
from typing import List, Dict
from duckduckgo_search import DDGS

@tool_registry.register

def search_web(query:str, max_results:int=3)->str:
    """
    Search the live web for techincal documentation , papers and recent news.
    """

    try:
        with DDGS() as ddgs:
            results: List[Dict[str,str]] = list(ddgs.text(query, max_results=max_results))

        if not results:
            return f"NO live search result found for query: '{query}'"

        formatted_results = [f"[Live web Results for {query}]:\n"]

        for idx , res in enumerate(results,1):
            title = res.get("title","No title")
            snippet = res.get("body", "No Description")
            url = res.get("href", "NO url")
            formatted_results.append(f"{idx}. Title: {title}\n   Snippet: {snippet}\n   URL: {url}\n")

        return "\n".join(formatted_results)
    except Exception as e:
        return f"Error  executing live search for '{query}' : {str(e)}"

