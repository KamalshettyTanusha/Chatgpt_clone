import requests

from bs4 import BeautifulSoup

from langchain_core.tools import tool


@tool("live_web_search")
def live_web_search(
    query: str
) -> str:
    """
    Search the live web using DuckDuckGo.

    Use this tool ONLY when external web information
    is genuinely required.

    Appropriate uses include:

    - current information
    - recent information
    - latest news
    - current public office holders
    - current events
    - information about a person that needs external
      verification
    - facts that are not reliably available from
      the model's existing knowledge
    - explicit requests to search the web

    Do NOT use this tool merely to answer:

    - definitions
    - meanings
    - full forms
    - basic concepts
    - common terminology
    - simple programming questions
    - general knowledge that you can answer confidently

    For example:

        "What is the full form of RAG?"

    should normally NOT call this tool.

    If a user asks a question involving multiple
    independent sources, this tool may be combined
    with other tools.

    Example:

        "Do I and Donald Trump have common hobbies?"

    The agent may retrieve the user's hobbies from
    memory and use this tool to research Donald Trump's
    hobbies, then combine the results.

    Args:
        query: Search query.
    """

    if not query or not query.strip():
        return "Search query is required."

    try:

        headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/138.0.0.0 Safari/537.36"
            )
        }

        response = requests.get(
            "https://html.duckduckgo.com/html/",
            params={
                "q": query.strip()
            },
            headers=headers,
            timeout=10,
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        results = []

        for result in soup.select(
            ".result"
        )[:5]:

            title = result.select_one(
                ".result__a"
            )

            snippet = result.select_one(
                ".result__snippet"
            )

            if title:

                results.append(
                    {
                        "title": title.get_text(
                            strip=True
                        ),
                        "link": title.get(
                            "href"
                        ),
                        "snippet": (
                            snippet.get_text(
                                " ",
                                strip=True
                            )
                            if snippet
                            else ""
                        ),
                    }
                )

        if not results:
            return "No search results found."

        formatted_results = []

        for result in results:

            formatted_results.append(
                (
                    f"Title: {result['title']}\n"
                    f"URL: {result['link']}\n"
                    f"Snippet: {result['snippet']}"
                )
            )

        return "\n\n".join(
            formatted_results
        )

    except requests.RequestException as e:

        return (
            f"Web search request failed: {str(e)}"
        )

    except Exception as e:

        return (
            f"Web search error: {str(e)}"
        )