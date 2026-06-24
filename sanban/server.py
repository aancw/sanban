"""Sanban server — runs REST API and/or MCP server."""
from __future__ import annotations

import argparse
import sys
import threading

import uvicorn

from sanban.rest import app
from sanban.mcp_server import mcp


def main():
    sys.stderr.reconfigure(line_buffering=True)
    parser = argparse.ArgumentParser(description="sanban — simple kanban")
    parser.add_argument("--host", default="0.0.0.0", help="REST host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8900, help="REST port (default: 8900)")
    parser.add_argument("--mcp-only", action="store_true", help="MCP stdio only (for agent config)")
    parser.add_argument("--rest-only", action="store_true", help="REST + web UI only")
    args = parser.parse_args()

    if args.mcp_only:
        mcp.run(transport="stdio")
        return

    if args.rest_only:
        uvicorn.run(app, host=args.host, port=args.port, log_level="info")
        return

    # Default: REST + web UI
    print(f"sanban REST API on http://{args.host}:{args.port}", file=sys.stderr, flush=True)
    print(f"Board data in ~/.sanban/boards/", file=sys.stderr, flush=True)
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
