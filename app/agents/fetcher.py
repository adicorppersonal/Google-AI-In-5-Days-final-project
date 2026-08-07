from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types
from google.adk.agents.callback_context import CallbackContext
from app.tools import google_web_search, SearchInput
from app.config import FAST_MODEL

async def fetcher_callback(callback_context: CallbackContext):
    # Ensure sanitized query is available in state or context for native tool usage
    query = callback_context.state.get("sanitized_query")
    if not query:
        for event in reversed(callback_context.session.events):
            if event.author == "user":
                query = event.content.parts[0].text if event.content.parts else "AI/ML news"
                break
    if not query:
        query = "AI/ML intelligence brief"
    callback_context.state["current_query"] = query

fetcher_agent = Agent(
    name="fetcher_agent",
    model=Gemini(model=FAST_MODEL, retry_options=types.HttpRetryOptions(attempts=3)),
    instruction="""You are the Fetcher Agent. You have access to the native tool `google_web_search`.
1. Retrieve the search query from context or state (e.g. current query).
2. Call the native `google_web_search` tool with explicit SearchInput parameters to fetch news and query vector memory.
3. Structure and present the fetched articles cleanly for the Summarizer Agent.""",
    tools=[google_web_search],
    before_agent_callback=fetcher_callback,
    output_key="organized_articles"
)
