import asyncio
from model import SearchInput, SearchResult
from model import SearchResult

async def search_tool(query: SearchInput):
    print('----------------------')
    print('Search Tools')
    print(f'Query   : {query.query}')
    print(f'Max Results: {query.max_result}')
    print('----------------------')

    await asyncio.sleep(1)

    return SearchResult(
        articles = [
            f"Latest result about '{query.query}'",
            "OpenAI announced new AI models",
            "Google released new AI research",
            "NVIDIA reported AI chip Growth"
        ]
    )