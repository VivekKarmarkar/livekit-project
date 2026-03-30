#!/usr/bin/env bun
/**
 * Robo Voice Channel — MCP server with Channel capability
 *
 * Claude Code spawns this as a subprocess. It bridges between:
 * - Claude Code (via stdio JSON-RPC + channel notifications)
 * - The LiveKit agent (via HTTP on localhost:7890)
 *
 * Flow:
 * 1. Agent POSTs transcribed voice to /transcription
 * 2. Server pushes it to Claude Code via channel notification
 * 3. Claude Code calls the `speak` tool with response text
 * 4. Server returns the text as the HTTP response to step 1
 * 5. Agent receives it and sends to TTS
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js'
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'
import {
  ListToolsRequestSchema,
  CallToolRequestSchema,
} from '@modelcontextprotocol/sdk/types.js'

const PORT = 7890

// --- Async rendezvous: pending HTTP request waits for speak tool call ---
let pendingResolve: ((text: string) => void) | null = null
let messageCounter = 0

// --- MCP Server with channel capability ---
const mcp = new Server(
  { name: 'robo-voice', version: '0.1.0' },
  {
    capabilities: {
      tools: {},
      experimental: { 'claude/channel': {} },
    },
    instructions:
      'Voice transcriptions arrive as <channel source="robo-voice" user="voice" message_id="...">. ' +
      'The sender hears speech through a voice agent, not this terminal. ' +
      'Anything you want them to hear must go through the speak tool — ' +
      'your transcript output never reaches the voice interface.\n\n' +
      'Keep responses concise and conversational — they will be spoken aloud via TTS. ' +
      'Avoid markdown formatting, code blocks, and long lists in speak tool calls ' +
      'unless the user specifically asks. Reply with the speak tool for every voice message.',
  },
)

// --- Tool: "speak" — Claude Code calls this to send text to TTS ---
mcp.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'speak',
      description:
        'Send a spoken response to the voice user. The text will be synthesized to speech and played through their speaker.',
      inputSchema: {
        type: 'object' as const,
        properties: {
          text: {
            type: 'string',
            description: 'The text to speak aloud. Keep it conversational.',
          },
        },
        required: ['text'],
      },
    },
  ],
}))

mcp.setRequestHandler(CallToolRequestSchema, async (req) => {
  if (req.params.name === 'speak') {
    const { text } = req.params.arguments as { text: string }

    // Resolve the pending HTTP request from the agent
    if (pendingResolve) {
      pendingResolve(text)
      pendingResolve = null
    } else {
      // No pending request — log to stderr (stdout is sacred)
      process.stderr.write(
        `[robo-voice] speak called with no pending request: "${text.slice(0, 50)}..."\n`
      )
    }

    return { content: [{ type: 'text' as const, text: 'spoken' }] }
  }

  throw new Error(`unknown tool: ${req.params.name}`)
})

// --- Connect to Claude Code via stdio ---
await mcp.connect(new StdioServerTransport())

// Log to stderr only — stdout is for JSON-RPC
process.stderr.write(`[robo-voice] MCP channel server started, HTTP on port ${PORT}\n`)

// --- HTTP server: agent sends transcriptions, gets responses ---
Bun.serve({
  port: PORT,
  hostname: '127.0.0.1',
  idleTimeout: 120, // 2 min — Claude Code might take a while to think

  async fetch(req: Request): Promise<Response> {
    const url = new URL(req.url)

    // Health check
    if (req.method === 'GET' && url.pathname === '/health') {
      return new Response('ok')
    }

    // Agent posts transcribed voice text
    if (req.method === 'POST' && url.pathname === '/transcription') {
      const userText = await req.text()
      if (!userText.trim()) {
        return new Response('empty', { status: 400 })
      }

      messageCounter++
      const messageId = `m${messageCounter}`

      // Push to Claude Code via channel notification
      await mcp.notification({
        method: 'notifications/claude/channel',
        params: {
          content: userText,
          meta: {
            user: 'voice',
            message_id: messageId,
            ts: new Date().toISOString(),
          },
        },
      })

      process.stderr.write(`[robo-voice] pushed transcription #${messageId}: "${userText.slice(0, 60)}"\n`)

      // Wait for Claude Code to call the speak tool (blocks until response)
      const responseText = await new Promise<string>((resolve) => {
        pendingResolve = resolve

        // Timeout after 90 seconds
        setTimeout(() => {
          if (pendingResolve === resolve) {
            pendingResolve = null
            resolve('[No response from Claude Code — timed out]')
          }
        }, 90_000)
      })

      process.stderr.write(`[robo-voice] got response for #${messageId}: "${responseText.slice(0, 60)}"\n`)

      return new Response(responseText)
    }

    return new Response('not found', { status: 404 })
  },
})
