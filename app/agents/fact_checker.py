from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types

MODEL = "gemini-3.6-flash"

fact_checker_agent = Agent(
    name="fact_checker_agent",
    model=Gemini(model=MODEL, retry_options=types.HttpRetryOptions(attempts=3)),
    instruction="You are the Fact-Checker & Refiner Agent. Review the draft report: {draft_report}. Fact-check all claims against original data, refine the prose, correct any inaccuracies, and produce the refined summary/report under output_key 'draft_report'.",
    output_key="draft_report"
)
