# Robo Chat

A voice chatbot with a cute animated orange robot avatar, powered by LiveKit and the OpenAI Realtime API. Talk to Robo about anything — it speaks, listens, thinks, and shows you visual content when words aren't enough.

## Features

- **Voice conversation** — real-time voice chat using OpenAI's Realtime API (audio-in, audio-out, no separate STT/TTS pipeline)
- **Animated robot avatar** — custom SVG robot with expressive LED eyes, animated mouth, and a chest indicator light that reacts to conversation state (speaking, listening, thinking, idle)
- **Visual mode** — toggle a side panel where Robo can display markdown, LaTeX equations, code blocks, tables, and images while talking
- **Multilingual** — speaks and understands multiple languages natively (tested with Hindi, Marathi, Punjabi, Bengali, and more)
- **Dark mode** — forced dark theme for comfortable use

## Getting Started

### Prerequisites

- Python 3.11+ (installed automatically via `uv` if needed)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager
- Node.js 20+ with [pnpm](https://pnpm.io/installation)
- A [LiveKit Cloud](https://cloud.livekit.io/) account (free tier: 1,000 session minutes/month)
- An [OpenAI API key](https://platform.openai.com/api-keys)

### Installation

```bash
cd python-agents-examples/complex-agents/avatars/anam

# Agent backend
cd agent-py
uv sync --python 3.12
cd ..

# Frontend
cd frontend
pnpm install
cd ..
```

### Configuration

Create `.env.local` files from the examples:

**Agent** (`agent-py/.env.local`):
```
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_key
LIVEKIT_API_SECRET=your_secret
OPENAI_API_KEY=your_openai_key
```

**Frontend** (`frontend/.env.local`):
```
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_key
LIVEKIT_API_SECRET=your_secret
AGENT_NAME=Robo-Intake
```

Get your LiveKit credentials from the [LiveKit Cloud dashboard](https://cloud.livekit.io/) under Settings > API Keys.

### Running

Start both processes:

```bash
# Terminal 1 — Agent
cd agent-py
uv run python src/agent.py dev

# Terminal 2 — Frontend
cd frontend
pnpm dev
```

Open http://localhost:3000, click **Start chatting**, and talk to Robo.

## How It Works

```
You speak ──→ LiveKit (WebRTC) ──→ OpenAI Realtime API ──→ LiveKit ──→ You hear Robo
                                         │
                                         ├─ show_content() ──→ RPC ──→ Visual pane
                                         └─ voice response
```

- **LiveKit Cloud** handles real-time audio transport via WebRTC
- **OpenAI Realtime API** processes audio directly — no separate STT→LLM→TTS chain
- The agent pushes visual content to the frontend via **LiveKit RPC** when the conversation calls for it
- The robot avatar is rendered entirely client-side as an animated SVG, driven by LiveKit's `useVoiceAssistant` hook

## Project Structure

```
python-agents-examples/complex-agents/avatars/anam/
├── agent-py/
│   └── src/agent.py              # Voice agent with show_content tool
├── frontend/
│   ├── components/app/
│   │   ├── robot-avatar.tsx      # Animated SVG robot
│   │   ├── avatar-panel.tsx      # Robot display + controls
│   │   ├── visual-pane.tsx       # Markdown/LaTeX renderer
│   │   ├── session-view.tsx      # Chat/visual mode toggle
│   │   └── welcome-view.tsx      # Landing page
│   └── app/
│       └── layout.tsx            # Dark mode, header
└── README.md
```

## Tech Stack

- **Agent**: Python 3.12, LiveKit Agents SDK, OpenAI Realtime API
- **Frontend**: Next.js 15, React 19, Tailwind CSS, react-markdown, KaTeX
- **Transport**: LiveKit Cloud (WebRTC)
- **Voice AI**: OpenAI Realtime API (single model for speech understanding + generation)

## License

Based on [LiveKit's example agents](https://github.com/livekit-examples/python-agents-examples). See individual LICENSE files for details.
