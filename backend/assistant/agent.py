from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    noise_cancellation,
)
from livekit.plugins import google
from .prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from .tools import get_weather, search_web, send_email
load_dotenv()


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTION,
            llm=google.beta.realtime.RealtimeModel(
                voice="Kore",
                temperature=0.8,
                modalities=["text", "audio"],  # Enable both text and audio
            ),
            tools=[
                get_weather,
                search_web,
                send_email
            ],
        )

async def entrypoint(ctx: agents.JobContext):
    # Create the assistant agent
    assistant = Assistant()
    
    # Create session with proper configuration
    session = AgentSession(
        agent=assistant,
        room=ctx.room,
        room_input_options=RoomInputOptions(
            # Enable voice input and output
            video_enabled=False,  # We only need audio for this use case
            audio_enabled=True,
            # LiveKit Cloud enhanced noise cancellation
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Start the session
    await session.start()

    # Connect to the room
    await ctx.connect()

    # Begin the conversation with the opening message
    await session.generate_reply(
        instructions=SESSION_INSTRUCTION,
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))