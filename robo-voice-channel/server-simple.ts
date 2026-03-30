#!/usr/bin/env bun
/**
 * Robo Voice Simple — MCP server with blocking speak_and_listen tool
 *
 * No Channels. No special flags. Just a blocking tool that exchanges text
 * between Claude Code and the LiveKit agent.
 *
 * Claude Code spawns this as a subprocess. It bridges between:
 * - Claude Code (via stdio JSON-RPC — standard MCP, no experimental features)
 * - The LiveKit agent (via HTTP on localhost:7890)
 *
 * Pattern (inspired by VoiceMode's converse tool):
 * 1. Claude Code calls speak_and_listen(text) — tool blocks
 * 2. Server stores the response text, waits for agent
 * 3. Agent POSTs transcribed voice to /transcription
 * 4. Server exchanges: agent gets Claude's text, tool gets user's transcription
 * 5. Agent sends Claude's text to TTS, tool returns transcription to Claude Code
 * 6. Claude Code processes, calls speak_and_listen again — loop continues
 *
 * This is a classic rendezvous/exchanger pattern: whichever side arrives
 * first waits for the other. When both are present, they swap data.
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js'
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'
import {
  ListToolsRequestSchema,
  CallToolRequestSchema,
} from '@modelcontextprotocol/sdk/types.js'

const PORT = 7890

// --- Exchanger: two slots, one for each side ---
// When Claude calls speak_and_listen, it deposits responseText and waits for userText.
// When the agent POSTs /transcription, it deposits userText and waits for responseText.
// Whichever arrives first waits. When both present, they swap.

let pendingTool: {
  responseText: string
  resolve: (transcription: string) => void
} | null = null

let pendingHttp: {
  userText: string
  resolve: (responseText: string) => void
} | null = null

function tryExchange(): void {
  if (pendingTool && pendingHttp) {
    // Both sides present — swap data
    pendingHttp.resolve(pendingTool.responseText) // agent gets Claude's response
    pendingTool.resolve(pendingHttp.userText) // Claude gets user's transcription
    pendingTool = null
    pendingHttp = null
  }
}

// --- MCP Server — standard tools only, no Channels ---
const mcp = new Server(
  { name: 'robo-voice', version: '0.2.0' },
  {
    capabilities: {
      tools: {},
      // No experimental/claude/channel — that's the whole point of simple mode
    },
    instructions:
      'You are connected to a voice agent named Robo. ' +
      'The user talks to you through Robo via speech.\n\n' +
      'To have a conversation, call the speak_and_listen tool in a loop:\n' +
      '1. Call speak_and_listen with your message — Robo will speak it aloud\n' +
      '2. The tool blocks until the user responds via voice\n' +
      '3. The tool returns the user\'s transcribed speech\n' +
      '4. Process their response and call speak_and_listen again\n\n' +
      'Start by calling speak_and_listen with a warm greeting.\n' +
      'Keep responses concise and conversational — they will be spoken aloud via TTS. ' +
      'Avoid markdown formatting, code blocks, and long lists unless the user specifically asks.',
  },
)

// --- Tool: "speak_and_listen" — blocking voice exchange ---
mcp.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'speak_and_listen',
      description:
        'Send a spoken response to the voice user and wait for their reply. ' +
        'The text will be synthesized to speech. The tool blocks until the user ' +
        'responds via voice, then returns their transcribed speech. ' +
        'Call this in a loop to maintain a conversation.',
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
  if (req.params.name === 'speak_and_listen') {
    const { text } = req.params.arguments as { text: string }

    process.stderr.write(
      `[robo-voice] speak_and_listen called: "${text.slice(0, 60)}..."\n`
    )

    // Deposit our side and wait for the agent
    const transcription = await new Promise<string>((resolve) => {
      pendingTool = { responseText: text, resolve }

      // Timeout after 120 seconds (generous — user might take a while to respond)
      setTimeout(() => {
        if (pendingTool?.resolve === resolve) {
          pendingTool = null
          resolve('[No response — timed out waiting for voice input]')
        }
      }, 120_000)

      // Check if agent is already waiting
      tryExchange()
    })

    process.stderr.write(
      `[robo-voice] got transcription: "${transcription.slice(0, 60)}"\n`
    )

    return {
      content: [{ type: 'text' as const, text: transcription }],
    }
  }

  throw new Error(`unknown tool: ${req.params.name}`)
})

// --- Connect to Claude Code via stdio ---
await mcp.connect(new StdioServerTransport())

process.stderr.write(
  `[robo-voice] Simple mode MCP server started, HTTP on port ${PORT}\n`
)

// --- HTTP server: agent sends transcriptions, gets responses ---
Bun.serve({
  port: PORT,
  hostname: '127.0.0.1',
  idleTimeout: 120,

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

      process.stderr.write(
        `[robo-voice] transcription received: "${userText.slice(0, 60)}"\n`
      )

      // Deposit our side and wait for Claude's response
      const responseText = await new Promise<string>((resolve) => {
        pendingHttp = { userText, resolve }

        // Timeout after 120 seconds
        setTimeout(() => {
          if (pendingHttp?.resolve === resolve) {
            pendingHttp = null
            resolve('[No response from Claude Code — timed out]')
          }
        }, 120_000)

        // Check if Claude is already waiting
        tryExchange()
      })

      process.stderr.write(
        `[robo-voice] sending response to agent: "${responseText.slice(0, 60)}"\n`
      )

      return new Response(responseText)
    }

    return new Response('not found', { status: 404 })
  },
})
