import json
import logging
from typing import Annotated

from dotenv import load_dotenv
from pydantic import Field

from livekit import rtc
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    MetricsCollectedEvent,
    RunContext,
    cli,
    function_tool,
    llm,
    metrics,
    room_io,
)
from livekit.plugins import noise_cancellation, openai

logger = logging.getLogger("agent")

load_dotenv(".env.local")


def get_remote_participant_identity(ctx: JobContext) -> str:
    """Get the identity of the remote participant (user)."""
    for participant in ctx.room.remote_participants.values():
        return participant.identity
    raise llm.LLMToolException("No remote participant found")


async def perform_rpc_to_frontend(
    ctx: JobContext, method: str, payload: str
) -> str:
    """Perform an RPC call to the frontend participant."""
    local_participant = ctx.room.local_participant
    if not local_participant:
        raise llm.LLMToolException("Agent not connected to room")

    destination_identity = get_remote_participant_identity(ctx)

    response = await local_participant.perform_rpc(
        destination_identity=destination_identity,
        method=method,
        payload=payload,
        response_timeout=5.0,
    )
    return response


class RoboAssistant(Agent):
    def __init__(self, ctx: JobContext) -> None:
        self._ctx = ctx
        super().__init__(
            instructions="""You are Robo, a cute and friendly AI assistant. You chat with users about any topic they want.

            Conversation style:
            - Speak in short, natural sentences.
            - Be warm, curious, and fun.
            - You have a playful personality but you're also knowledgeable.
            - Do not use markdown, emojis, asterisks, or stage directions.
            - Keep responses concise since this is a voice conversation.

            Visual content:
            - You have a visual panel that can display rich content to the user.
            - When explaining something that benefits from visuals, use the show_content tool.
            - For math and equations: use ONLY LaTeX in the show_content tool. Do NOT mix text with LaTeX. Put all equations in display math ($$...$$) blocks. Explain the equations verbally while showing pure LaTeX on the panel.
            - For code: use fenced code blocks with the language specified.
            - For diagrams: use ASCII box-drawing characters in a code block. Use Unicode characters like ┌─┐│└─┘ for boxes, ──▶ for arrows, ├── └── │ for trees. Keep diagrams simple with uniform box widths. For flowcharts use vertical flows (easier to align than horizontal). For hierarchies use indented tree format with ├── └── │ connectors.
            - For notes and summaries: use plain text with markdown formatting (headings, bullet points, bold, etc.). Use this when the user asks you to write down notes, key points, or summaries.
            - Keep show_content output clean and focused. You explain things with your voice, the panel shows the visuals or notes.
            - Only use show_content when it genuinely helps — don't use it for simple chat.""",
        )

    @function_tool
    async def show_content(
        self,
        context: RunContext,
        content: Annotated[
            str,
            Field(
                description="Markdown content to display in the visual panel. Supports headings, lists, code blocks, tables, images via URL, and LaTeX math (use $$ for display math, $ for inline)."
            ),
        ],
    ):
        """Show visual content (markdown) in the user's visual panel. Use this when explaining something that benefits from visuals like equations, diagrams, code, tables, or structured information."""
        try:
            payload = json.dumps({"content": content})
            response = await perform_rpc_to_frontend(self._ctx, "showContent", payload)
            return response
        except Exception as e:
            raise llm.LLMToolException(f"Failed to show content: {str(e)}")


server = AgentServer()



@server.rtc_session(agent_name="Robo-Intake")
async def intake_agent(ctx: JobContext):
    # Logging setup
    # Add any other context you want in all log entries here
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Join the room and connect to the user before starting avatar/session
    await ctx.connect()

    session = AgentSession(
        llm=openai.realtime.RealtimeModel(voice="coral"),
    )

    # Metrics collection, to measure pipeline performance
    # For more information, see https://docs.livekit.io/deploy/observability/data/
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def on_metrics_collected(ev: MetricsCollectedEvent) -> None:
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # Start the session first, which initializes the voice pipeline and warms up the models
    await session.start(
        agent=RoboAssistant(ctx),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: (
                    noise_cancellation.BVCTelephony()
                    if params.participant.kind
                    == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                    else noise_cancellation.BVC()
                ),
            ),
        ),
    )

    # Greet the patient and begin intake
    session.generate_reply(
        instructions="Greet the user warmly and ask what they'd like to chat about."
    )


if __name__ == "__main__":
    cli.run_app(server)
