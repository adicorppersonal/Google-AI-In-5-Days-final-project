import re
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types
from google.adk.agents.callback_context import CallbackContext

MODEL = "gemini-3.6-flash"

def redact_pii(text: str) -> str:
    """Programmatically redacts personal identifiable information (PII) such as emails, phones, SSNs, and credit cards from text.

    Args:
        text: Raw user input text.

    Returns:
        Sanitized text with PII replaced by redaction placeholders.
    """
    if not text:
        return ""
    
    # Redact email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[REDACTED_EMAIL]', text)
    
    # Redact phone numbers (various formats)
    text = re.sub(r'\b(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})\b', '[REDACTED_PHONE]', text)
    
    # Redact Social Security Numbers (SSN)
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED_SSN]', text)
    
    # Redact 13-16 digit credit card numbers
    text = re.sub(r'\b(?:\d[ -]*?){13,16}\b', '[REDACTED_CREDIT_CARD]', text)
    
    return text

async def redactor_callback(callback_context: CallbackContext):
    user_input = ""
    for event in reversed(callback_context.session.events):
        if event.author == "user":
            user_input = event.content.parts[0].text if event.content.parts else ""
            break
    
    redacted_text = redact_pii(user_input)
    callback_context.state["redacted_input"] = redacted_text

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
