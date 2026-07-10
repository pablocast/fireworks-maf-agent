"""Simple chat agent using Microsoft Agent Framework.

- Talks to a Fireworks AI deployment through the OpenAI-compatible API.
- Uses the Fireworks Docs MCP server (https://docs.fireworks.ai/mcp) as a tool,
  so the agent can search the full Fireworks AI documentation.
"""

import asyncio
import os

from agent_framework import MCPStreamableHTTPTool
from agent_framework.openai import OpenAIChatClient
from agent_framework_foundry_hosting import ResponsesHostServer
from dotenv import load_dotenv

load_dotenv()


# Fireworks exposes an OpenAI-compatible endpoint.
FIREWORKS_BASE_URL = os.getenv("FIREWORKS_BASE_URL", "https://api.fireworks.ai/inference/v1")
FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY")
FIREWORKS_MODEL = os.getenv("FIREWORKS_MODEL", "accounts/fireworks/models/llama-v3p3-70b-instruct")

INSTRUCTIONS = (
    "You are a helpful assistant that answers questions about Fireworks AI. "
    "When a question is about Fireworks features, APIs, deployments, or configuration, "
    "use the Fireworks documentation tools to look up accurate, up-to-date information "
    "before answering. Cite the relevant docs when useful."
)

async def main() -> None:
    if not FIREWORKS_API_KEY:
        raise SystemExit(
            "FIREWORKS_API_KEY is not set. Add it to your .env file (see .env for the template)."
        )

    chat_client = OpenAIChatClient(
        model=FIREWORKS_MODEL,
        api_key=FIREWORKS_API_KEY,
        base_url=FIREWORKS_BASE_URL,
    )

    # Fireworks Docs MCP server (streamable HTTP transport).
    async with MCPStreamableHTTPTool(
        name="fireworks-docs",
        url="https://docs.fireworks.ai/mcp",
    ) as fireworks_docs:
        agent = chat_client.as_agent(
            name="FireworksDocsAgent",
            instructions=INSTRUCTIONS,
            tools=fireworks_docs,
        )

        # Start the ResponsesHostServer to handle incoming requests.
        # Use run_async() because we are already inside a running event loop
        # (server.run() would call asyncio.run() again and fail).
        server = ResponsesHostServer(agent)
        await server.run_async()
    

if __name__ == "__main__":
    asyncio.run(main())
