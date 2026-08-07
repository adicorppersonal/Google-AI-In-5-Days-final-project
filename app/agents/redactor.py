from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types
from google.adk.agents.callback_context import CallbackContext
from app.tools import redact_pii, RedactionInput

MODEL = "gemini-3.6-flash"

async def redactor_callback(callback_context: CallbackContext):
    user_input = ""
    for event in reversed(callback_context.session.events):
        if event.author == "user":
            user_input = event.content.parts[0].text if event.content.parts else ""
            break
    
    redaction_input = RedactionInput(text=user_input)
    result = redact_pii(redaction_input)
    
    if result.get("error"):
        print(f"[Redaction Error] {result.get('error')}. Recovery: {result.get('recovery_instructions')}")
    
    callback_context.state["redacted_input"] = result.get("sanitized_text", "")

redactor_agent = Agent(
    name="redactor_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="You are the Custom Redactor Agent. Your sole responsibility is to intercept user prompts and programmatically redact any personal identifiable information (PII) before passing the sanitized prompt to the security gatekeeper.",
    before_agent_callback=redactor_callback,
    output_key="redacted_input"
)
