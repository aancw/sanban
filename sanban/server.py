"""Sanban server — runs REST API + MCP server."""
from __future__ import annotations

import argparse
import sys
import threading

import uvicorn

from sanban.rest import app
from sanban.mcp_server import mcp


def run_rest(host: str, port: int):
    uvicorn.run(app, host=host, port=port, log_level="info")


def run_mcp():
    mcp.run(transport="stdio")


def main():
    parser = argparse.ArgumentParser(description="sanban — kanban board with MCP + REST")
    parser.add_argument("--host", default="0.0.0.0", help="REST host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8900, help="REST port (default: 8900)")
    parser.add_argument("--mcp-only", action="store_true", help="Run MCP stdio server only (no REST)")
    parser.add_argument("--rest-only", action="store_true", help="Run REST server only (no MCP)")
    args = parser.parse_args()

    if args.mcp_only:
        run_mcp()
        return

    if args.rest_only:
        run_rest(args.host, args.port)
        return

    # Run both: MCP in a thread, REST in main thread
    mcp_thread = threading.Thread(target=run_mcp, daemon=True)
    mcp_thread.start()
    print(f"sanban MCP server running (stdio)", file=sys.stderr)
    print(f"sanban REST API running on http://{args.host}:{args.port}", file=sys.stderr)
    run_rest(args.host, args.port)


if __name__ == "__main__":
    main()
