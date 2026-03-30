import json
import logging
import os
from typing import Annotated

import aiohttp
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


CLAUDE_CODE_BRIDGE_URL = "http://127.0.0.1:7890"


class ClaudeCodeAssistant(Agent):
    """Agent that bridges voice to a live Claude Code session via MCP Channel."""

    def __init__(self, ctx: JobContext) -> None:
        self._ctx = ctx
        super().__init__(
            instructions="You are a voice interface to Claude Code. "
            "The llm_node handles all communication with Claude Code.",
        )

    async def llm_node(self, chat_ctx, tools, model_settings=None):
        """Override the LLM node to bridge to Claude Code via MCP Channel server."""

        async def bridge_stream():
            # Extract the user's latest message
            user_text = ""
            for msg in reversed(chat_ctx.messages()):
                if msg.role == "user":
                    user_text = msg.text_content or ""
                    break

            if not user_text:
                return

            logger.info(f"Claude Code bridge: sending '{user_text[:60]}'")

            try:
                async with aiohttp.ClientSession() as http:
                    async with http.post(
                        f"{CLAUDE_CODE_BRIDGE_URL}/transcription",
                        data=user_text,
                        timeout=aiohttp.ClientTimeout(total=90),
                    ) as resp:
                        if resp.status != 200:
                            yield "Sorry, I couldn't reach Claude Code."
                            return
                        response_text = await resp.text()

                logger.info(f"Claude Code bridge: got response '{response_text[:60]}'")
                yield response_text

            except aiohttp.ClientError as e:
                logger.error(f"Claude Code bridge error: {e}")
                yield "I can't connect to Claude Code right now."

        return bridge_stream()


server = AgentServer()


async def start_agent(ctx: JobContext, mode: str):
    """Shared agent startup logic for both modes."""
    ctx.log_context_fields = {"room": ctx.room.name}
    await ctx.connect()

    logger.info(f"Agent mode: {mode}")

    if mode == "claude-code":
        from livekit.plugins import deepgram, silero

        # Claude Code mode: STT + TTS with llm_node bridging to Claude Code
        # Use VAD turn detection (local, no LiveKit Inference needed)
        # Generous endpointing delays — Claude Code takes longer to respond
        session = AgentSession(
            stt=deepgram.STT(model="nova-3", language="multi"),
            llm=openai.LLM(model="gpt-4o-mini"),  # placeholder — llm_node overrides this
            tts=openai.TTS(voice="coral"),
            vad=silero.VAD.load(),
            turn_detection="vad",
            min_endpointing_delay=1.5,
            max_endpointing_delay=6.0,
        )
    elif mode == "pipeline":
        from livekit.plugins import deepgram, silero
        from livekit.plugins.turn_detector.multilingual import MultilingualModel

        session = AgentSession(
            stt=deepgram.STT(model="nova-3", language="multi"),
            llm=openai.LLM(model="gpt-4o-mini"),
            tts=openai.TTS(voice="coral"),
            vad=silero.VAD.load(),
            turn_detection=MultilingualModel(),
            preemptive_generation=True,
        )
    else:
        session = AgentSession(
            llm=openai.realtime.RealtimeModel(voice="coral"),
        )

    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def on_metrics_collected(ev: MetricsCollectedEvent) -> None:
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    agent = ClaudeCodeAssistant(ctx) if mode == "claude-code" else RoboAssistant(ctx)

    await session.start(
        agent=agent,
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

    session.generate_reply(
        instructions="Greet the user warmly and ask what they'd like to chat about."
    )


@server.rtc_session(agent_name="Robo-Intake")
async def robo_agent(ctx: JobContext):
    # Mode from job metadata (set by frontend dispatch), fallback to env var
    mode = os.environ.get("AGENT_MODE", "realtime").lower()
    job_meta = ctx.job.metadata
    logger.info(f"Job metadata: '{job_meta}'")
    if job_meta:
        try:
            meta = json.loads(job_meta)
            if meta.get("agent_mode"):
                mode = meta["agent_mode"]
        except (json.JSONDecodeError, AttributeError):
            pass
    logger.info(f"Agent mode: {mode}")
    await start_agent(ctx, mode)


if __name__ == "__main__":
    cli.run_app(server)
