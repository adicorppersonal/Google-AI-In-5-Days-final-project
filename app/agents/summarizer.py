from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types
from app.config import FAST_MODEL

summarizer_agent = Agent(
    name="summarizer_agent",
    model=Gemini(model=FAST_MODEL, retry_options=types.HttpRetryOptions(attempts=3)),
    instruction="You are the Summarizer Agent (the speed reader). Take the organized articles from: {organized_articles} and create short summaries using Gemini API context understanding. Each summary must be strictly 2-3 sentences long.",
    output_key="article_summaries"
)
