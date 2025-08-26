from dotenv import load_dotenv
import sys
import os

# Add the parent directory to Python path to allow importing voice_assistant
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from .env
load_dotenv()

# LiveKit agent libraries
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import noise_cancellation
from livekit.plugins import google

# Absolute imports from your voice_assistant package
from assistant.prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from assistant.tools import get_weather, search_web, send_email


# Define your assistant agent
class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTION,
            llm=google.beta.realtime.RealtimeModel(
                voice="Kore",
                temperature=0.7,  # Slightly lower for more consistent responses
                modalities=["text", "audio"],  # Enable both text and audio
            ),
            tools=[
                get_weather,
                search_web,
                send_email
            ],
        )


# Define the job entrypoint
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


# Launch the agent worker
if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
