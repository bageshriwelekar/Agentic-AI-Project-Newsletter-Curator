"""
Agent 1: Story Researcher
=========================
Input  : topic (str), num_results (int)
Action : Calls Tavily Search API with multiple query variants
         to fetch the week's most relevant stories
Output : List of story dicts [{title, url, snippet, published_date}]
"""

import os
from dotenv import load_dotenv

load_dotenv()


def research_stories(topic: str, num_results: int = 12) -> list[dict]:
    """
    Agent 1 — Story Researcher

    Uses Tavily Search to find recent, relevant stories for the given topic.
    Runs 3 different query variants to maximise coverage, then deduplicates.
    """
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

        queries = [
            f"{topic} latest news this week",
            f"{topic} recent developments 2025",
            f"top stories {topic} trends",
        ]

        all_stories = []
        seen_urls = set()

        for query in queries:
            try:
                results = client.search(
                    query=query,
                    search_depth="advanced",
                    max_results=6,
                    include_answer=False,
                )
                for r in results.get("results", []):
                    url = r.get("url", "")
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        all_stories.append(
                            {
                                "title": r.get("title", "Untitled"),
                                "url": url,
                                "snippet": r.get("content", "")[:350],
                                "published_date": r.get("published_date", "Recent"),
                            }
                        )
            except Exception as e:
                print(f"[Researcher] Query failed: {query} — {e}")
                continue

        return all_stories[:num_results]

    except Exception as e:
        print(f"[Researcher] Fatal error: {e}")
        # Fallback demo data so the app doesn't crash during testing
        return [
            {
                "title": f"Sample Story about {topic} #1",
                "url": "https://example.com/story1",
                "snippet": f"This is a sample story about {topic}. Add your real Tavily API key to get live results.",
                "published_date": "2025",
            },
            {
                "title": f"Sample Story about {topic} #2",
                "url": "https://example.com/story2",
                "snippet": f"Another sample story about {topic}. Configure TAVILY_API_KEY in your .env file.",
                "published_date": "2025",
            },
            {
                "title": f"Sample Story about {topic} #3",
                "url": "https://example.com/story3",
                "snippet": f"Third sample story covering {topic} developments. Real data requires Tavily API.",
                "published_date": "2025",
            },
        ]
