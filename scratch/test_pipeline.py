import asyncio
from google.adk.runners import InMemoryRunner
from google.genai import types
from app.agent import root_agent

async def main():
    runner = InMemoryRunner(agent=root_agent, app_name="app")
    session = await runner.session_service.create_session(app_name="app", user_id="test-user")
    print(f"Session created: {session.id}")
    
    msg = types.Content(role="user", parts=[types.Part.from_text(text="Generate daily AI/ML intelligence report")])
    async for event in runner.run_async(
        user_id="test-user",
        session_id=session.id,
        new_message=msg
    ):
        print(f"Event from {event.author}: {event.content}")

if __name__ == "__main__":
    asyncio.run(main())
