# Next Steps

1. Deleting redundant code files (partially done — hedra/lemonslice/tavus removed, kael.imx and 19 example folders remain)

2. Claude Code integration via MCP and Channels
   - Step A: Add visible toggle (isolated vs pipeline mode). Verify pipeline mode (STT+LLM+TTS) works with own API keys (Deepgram + OpenAI LLM + OpenAI TTS)
   - Step B: Swap OpenAI LLM for Anthropic LLM in pipeline mode (livekit-plugins-anthropic + ANTHROPIC_API_KEY)
   - Step C: Build Robo as an MCP server with Channel capability that Claude Code spawns as a subprocess
     - Robo pushes transcribed voice to Claude Code via `notifications/claude/channel` over stdout
     - Claude Code responds by calling a `speak` tool on the MCP server via stdin
     - The `speak` tool sends the response text to TTS → user hears it
     - No Anthropic API call needed — Claude Code IS the brain
     - STT and TTS are the only external services remaining in the pipeline
     - Tools: mcp-server-dev plugin (installed), fakechat source as template
     - Launch: claude --dangerously-load-development-channels server:robo-voice

3. ~~Record demos and upload to YouTube/Twitter~~ DONE
   - ~~Professor Claude long demo (Julia + Physics + ASCII diagrams)~~ DONE
   - ~~Professor Claude short demo~~ DONE
   - Both uploaded to Twitter and YouTube

4. Polished demo video based on the short and long demo recordings

5. Make project webpage with YouTube demo embeds and add to personal website
