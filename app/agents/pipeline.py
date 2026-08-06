from google.adk.agents import SequentialAgent, LoopAgent
from app.agents.redactor import redactor_agent
from app.agents.gatekeeper import security_gatekeeper_agent
from app.agents.fetcher import fetcher_agent
from app.agents.summarizer import summarizer_agent
from app.agents.reporter import reporter_agent
from app.agents.fact_checker import fact_checker_agent

# Refinement loop where fact-checker refines reporter agent's draft report (max 5 iterations)
refinement_loop = LoopAgent(
    name="refinement_loop",
    sub_agents=[reporter_agent, fact_checker_agent],
    max_iterations=5
)

# Complete pipeline: Redactor (PII) -> Security Gatekeeper -> Fetcher -> Summarizer -> Refinement Loop
news_pipeline = SequentialAgent(
    name="news_pipeline",
    sub_agents=[
        redactor_agent,
        security_gatekeeper_agent,
        fetcher_agent,
        summarizer_agent,
        refinement_loop
    ]
)
