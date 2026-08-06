from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types

MODEL = "gemini-3.6-flash"

reporter_agent = Agent(
    name="reporter_agent",
    model=Gemini(model=MODEL, retry_options=types.HttpRetryOptions(attempts=3)),
    instruction="You are the Reporter Agent (the editor). Pull everything together into one comprehensive report based on the article summaries: {article_summaries}. Create an Executive Summary, add detailed analysis and trends, and make sense of all the data.",
    output_key="draft_report"
)
