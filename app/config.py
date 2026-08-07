"""
Centralized configuration for Tiered Strategic Model Routing.
Balances cost, speed, and intelligence across multi-agent workflows.
"""

# Low-latency utility model for high-throughput, fast tasks (Redaction, Gatekeeping, Fetching, Summarizing)
FAST_MODEL = "gemini-3.6-flash"

# High-reasoning capability model for complex planning, editorial synthesis, and fact-checking (Reporting, Refinement)
REASONING_MODEL = "gemini-3.1-pro-preview"
