# server.py -- MCP server that gives an AI agent access to time.

import time
import datetime
import sys

from mcp.server.mcpserver import MCPServer

mcp = MCPServer("patience-mcp")


###

# NOTE: with the stdio transport, never print() to stdout in this file --
# stdout is the MCP protocol channel. Use stderr instead.
def print(*values: object, sep: str | None = " ", end: str | None = "\n"):
    if sep is None:
        sep = " "
    if end is None:
        end = "\n"
    sys.stderr.write(sep.join(str(v) for v in values))
    sys.stderr.write(end)


### Global State

t_between_calls = None

### Tools

@mcp.tool()
def approximate_tool_call_inference_overhead() -> str:
    """Call this tool twice, back-to-back as a pair."""
    """The value return from the second call is the real-world time elapsed between calls."""
    """This can inform a model of how much delay is caused by its own thoughts and inferencing between time-sensitive calls."""

    global t_between_calls
    
    if not t_between_calls:
        t_between_calls = time.time()
        return f"(Call again immediately)"
    else:
        elapsed = time.time() - t_between_calls
        t_between_calls = None
        return f"Back to back calls took {round(elapsed, 2)} seconds"


@mcp.tool()
def wait_for_seconds(ts: float) -> str:
    """Blocking wait for a number of seconds. Limited to one minute."""
    """Returns the actual time elapsed since the function was called."""

    ts = max(0, min(ts, 60))
    start: float = time.time()
    time.sleep(ts)
    finish: float = time.time()
    elapsed = finish - start
    return f"{round(elapsed, 2)} seconds elapsed."


@mcp.tool()
def wait_until_local_time(hour: int, minute: int, second: int) -> str:
    """Blocking wait until the given time (24-hour format)."""
    """Ignores any timezone changes, including DST."""
    """Returns when the time has elapsed, or if there is an error."""

    if not hour in range(0, 24):
        return "Invalid hour; range: 0-23. No time has elapsed."
    if not minute in range(0, 60):
        return "Invalid minute; range: 0-59. No time has elapsed."
    if not second in range(0, 60):
        return "Invalid second; range: 0-59. No time has elapsed."

    t_now = datetime.datetime.now().replace(microsecond=0)
    t_target = t_now.replace(hour=hour, minute=minute, second=second)

    # check if t_target is in the past, and if so, add a whole day
    # (any given time only appears once per day ...barring DST)
    if t_now > t_target:
        t_target += datetime.timedelta(days=1)

    #t_wait = (t_target - t_now).total_seconds()

    while (t_target.timestamp() - time.time()) > 0:
        # todo: improve performance without making a DST or other edge case
        time.sleep(1)
    
    return f"The time is now {datetime.datetime.now().isoformat(sep=' ', timespec='seconds')}"


if __name__ == "__main__":
    mcp.run()  # stdio transport by default
