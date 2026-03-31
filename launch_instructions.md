# Robo Voice — Global Launch Instructions

Connect Robo Voice to any Claude Code project session in 5 steps.

## Steps

1. **Start agent + frontend** from the livekit-project directory:
   ```bash
   cd ~/Python\ Files/livekit-project/python-agents-examples/complex-agents/avatars/anam/agent-py
   uv run python src/agent.py dev
   ```
   ```bash
   cd ~/Python\ Files/livekit-project/python-agents-examples/complex-agents/avatars/anam/frontend
   pnpm dev
   ```

2. **Exit the livekit-project Claude Code session** (frees port 7890 for the target session)

3. **cd into any project folder**:
   ```bash
   cd ~/some-other-project
   ```

4. **Launch Claude Code with the channels flag**:
   ```bash
   claude --dangerously-load-development-channels server:robo-voice
   ```

5. **Connect from the frontend** (http://localhost:3000) — select **claude-code** mode and talk

## Session management flags

All three work with the channels flag — just re-pass the channels flag every time:

```bash
# Named session
claude --dangerously-load-development-channels server:robo-voice --name my-session

# Continue most recent session
claude --dangerously-load-development-channels server:robo-voice --continue

# Resume by name or pick from list
claude --dangerously-load-development-channels server:robo-voice --resume my-session
claude --dangerously-load-development-channels server:robo-voice --resume
```

## Important notes

- The channels flag is **ephemeral** — it must be re-passed every launch
- Only **one session at a time** can use Robo Voice (port 7890 is single-slot)
- The livekit-project session must be exited first to free the MCP server port
