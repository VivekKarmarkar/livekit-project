#!/usr/bin/env bun
/**
 * Robo Voice Simple — MCP server with listen + speak tools
 *
 * No Channels. No special flags. Same turn-mapping as Channels mode.
 *
 * Pattern:
 * 1. Claude calls listen() — blocks until the user speaks
 * 2. Agent POSTs transcription — listen returns it, HTTP stays open
 * 3. Claude processes the transcription
 * 4. Claude calls speak(text) — resolves the open HTTP request
 * 5. Agent gets the response, sends to TTS
 * 6. Claude calls listen() again — loop continues
 *
 * This gives the SAME direct mapping as Channels mode:
 * the agent's POST for message N gets the response to message N back.
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js'
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'
import {
  ListToolsRequestSchema,
  CallToolRequestSchema,
} from '@modelcontextprotocol/sdk/types.js'

const PORT = 7890

// --- State: two independent rendezvous points ---

// When the agent POSTs a transcription:
//   - If Claude is already waiting in listen(), deliver immediately
//   - Otherwise queue it until Claude calls listen()
// The HTTP request stays open until Claude calls speak().

let pendingListen: ((text: string) => void) | null = null // Claude waiting for transcription
let pendingHttp: ((text: string) => void) | null = null // Agent waiting for response
let queuedTranscription: string | null = null // Transcription arrived before listen()

// --- MCP Server — standard tools only, no Channels ---
const mcp = new Server(
  { name: 'robo-voice', version: '0.2.0' },
  {
    capabilities: {
      tools: {},
    },
    instructions:
      'You are connected to a voice agent named Robo. ' +
      'The user talks to you through Robo via speech.\n\n' +
      'To have a conversation, use listen and speak in a loop:\n' +
      '1. Call listen — blocks until the user speaks, returns their transcription\n' +
      '2. Process their message\n' +
      '3. Call speak with your response — Robo speaks it aloud\n' +
      '4. Call listen again\n\n' +
      'Start by calling listen to wait for the user.\n' +
      'Keep responses concise and conversational — they will be spoken aloud via TTS. ' +
      'Avoid markdown formatting, code blocks, and long lists unless the user specifically asks.',
  },
)

// --- Tools: listen + speak ---
mcp.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'listen',
      description:
        'Wait for the voice user to speak. Blocks until they say something, ' +
        'then returns their transcribed speech. Call this before speak.',
      inputSchema: {
        type: 'object' as const,
        properties: {},
      },
    },
    {
      name: 'speak',
      description:
        'Send a spoken response to the voice user. The text will be synthesized ' +
        'to speech and played through their speaker. Call this after processing ' +
        'what listen returned.',
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
  if (req.params.name === 'listen') {
    process.stderr.write('[robo-voice] listen called — waiting for voice input\n')

    const transcription = await new Promise<string>((resolve) => {
      // Check if a transcription is already queued
      if (queuedTranscription) {
        const text = queuedTranscription
        queuedTranscription = null
        resolve(text)
        return
      }

      // Wait for agent to POST
      pendingListen = resolve

      // Timeout after 120 seconds
      setTimeout(() => {
        if (pendingListen === resolve) {
          pendingListen = null
          resolve('[No voice input — timed out after 120 seconds]')
        }
      }, 120_000)
    })

    process.stderr.write(
      `[robo-voice] listen got: "${transcription.slice(0, 60)}"\n`
    )

    return {
      content: [{ type: 'text' as const, text: transcription }],
    }
  }

  if (req.params.name === 'speak') {
    const { text } = req.params.arguments as { text: string }

    process.stderr.write(
      `[robo-voice] speak called: "${text.slice(0, 60)}"\n`
    )

    // Resolve the pending HTTP request from the agent
    if (pendingHttp) {
      pendingHttp(text)
      pendingHttp = null
    } else {
      process.stderr.write(
        '[robo-voice] speak called with no pending HTTP request\n'
      )
    }

    return { content: [{ type: 'text' as const, text: 'spoken' }] }
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

      // Deliver transcription to Claude's listen() call
      if (pendingListen) {
        pendingListen(userText)
        pendingListen = null
      } else {
        // Claude hasn't called listen() yet — queue it
        queuedTranscription = userText
      }

      // Now block until Claude calls speak() with the response
      const responseText = await new Promise<string>((resolve) => {
        pendingHttp = resolve

        // Timeout after 120 seconds
        setTimeout(() => {
          if (pendingHttp === resolve) {
            pendingHttp = null
            resolve('[No response from Claude Code — timed out]')
          }
        }, 120_000)
      })

      process.stderr.write(
        `[robo-voice] sending response to agent: "${responseText.slice(0, 60)}"\n`
      )

      return new Response(responseText)
    }

    return new Response('not found', { status: 404 })
  },
})
