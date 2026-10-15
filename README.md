# Patience-MCP

## Features

- A basic MCP server that lets agents explicitly delay for a period of time
- Delay for an amount of time, or until a specific time relative to the user
- It can also measure tool call timings caused by inferencing latency

## Use Case

I might use this for some fancy HIL stuff that has settling time. Pretty neat!

## Installation & Test

```bash
uv sync
mcp dev server.py