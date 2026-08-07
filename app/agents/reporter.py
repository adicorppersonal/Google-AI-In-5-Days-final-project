from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types
from google.adk.agents.callback_context import CallbackContext

MODEL = "gemini-3.6-flash"

async def hitl_approval_callback(callback_context: CallbackContext):
    """Human-in-the-Loop (HITL) code hook for high-stakes executive report finalization.
    
    Checks whether human approval has been granted in session state before allowing the
    Reporter Agent to finalize and publish the high-stakes intelligence brief.
    """
    approval_status = callback_context.state.get("human_approved", False)
    
    if not approval_status:
        # Pause invocation / request human review for high-stakes final report
        print("[HITL Security Gate] High-stakes action paused: Awaiting human sign-off on draft executive report.")
        callback_context.state["hitl_status"] = "pending_approval"
        callback_context.pause_invocation = True
    else:
        print("[HITL Security Gate] Human approval granted. Proceeding with report finalization.")
        callback_context.state["hitl_status"] = "approved"

reporter_agent = Agent(
    name="reporter_agent",
    model=Gemini(model=MODEL, retry_options=types.HttpRetryOptions(attempts=3)),
    instruction="You are the Reporter Agent (the editor). Pull everything together into one comprehensive report based on the article summaries: {article_summaries}. Create an Executive Summary, add detailed analysis and trends, and make sense of all the data.",
    before_agent_callback=hitl_approval_callback,
    output_key="draft_report"
)
