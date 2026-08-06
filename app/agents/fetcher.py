from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types
from google.adk.agents.callback_context import CallbackContext
from datetime import datetime
from zoneinfo import ZoneInfo
from app.db import save_article_to_storage

MODEL = "gemini-3.6-flash"

def google_web_search(query: str) -> dict:
    """Performs a web search using Google search simulation and stores retrieved articles into SQLite DB and CSV format.

    Args:
        query: Search topic or keywords.

    Returns:
        dict containing fetched articles with metadata.
    """
    now = datetime.now(ZoneInfo("UTC")).isoformat()
    search_results = [
        {
            "id": f"web-{int(datetime.now().timestamp())}-1",
            "title": f"Latest Developments in {query}: Agentic AI & Systems",
            "content": f"Recent industry reports on {query} highlight massive gains in multi-agent coordination, structured error recovery, and robust reasoning frameworks.",
            "timestamp": now,
        },
        {
            "id": f"web-{int(datetime.now().timestamp())}-2",
            "title": f"Production Scaling and Security for {query}",
            "content": f"Engineers deploying {query} report significant improvements when incorporating input sanitization, prompt injection guardrails, and persistent memory storage.",
            "timestamp": now,
        }
    ]

    stored_articles = []
    for art in search_results:
        word_count = len(art["content"].split())
        article_data = {
            "id": art["id"],
            "title": art["title"],
            "content": art["content"],
            "word_count": word_count,
            "timestamp": art["timestamp"],
        }
        # Store into local SQLite DB and CSV format
        save_article_to_storage(article_data, query)
        stored_articles.append(article_data)

    return {
        "status": "success",
        "query": query,
        "fetched_articles": stored_articles
    }

async def fetcher_callback(callback_context: CallbackContext):
    # Get sanitized query from gatekeeper or user message
    query = callback_context.state.get("sanitized_query")
    if not query:
        # Fallback to last user message
        for event in reversed(callback_context.session.events):
            if event.author == "user":
                query = event.content.parts[0].text if event.content.parts else "AI/ML news"
                break
    if not query:
        query = "AI/ML intelligence brief"

    # Execute search, store in SQLite & CSV, and save to state
    result = google_web_search(query)
    callback_context.state["organized_articles"] = result

fetcher_agent = Agent(
    name="fetcher_agent",
    model=Gemini(model=MODEL, retry_options=types.HttpRetryOptions(attempts=3)),
    instruction="You are the Fetcher Agent. Present and structure the fetched articles stored in state into a clean format for the Summarizer Agent.",
    before_agent_callback=fetcher_callback,
    output_key="organized_articles"
)
