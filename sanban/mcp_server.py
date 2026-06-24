"""MCP server for sanban — tools for agents to manage boards and items."""
from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from sanban import storage

mcp = FastMCP("sanban")


@mcp.tool()
def list_boards() -> str:
    """List all kanban boards."""
    boards = storage.list_boards()
    if not boards:
        return "No boards found."
    lines = [f"  {b['id']:12s}  {b['name']:20s}  {b['item_count']} items" for b in boards]
    return f"Boards:\n" + "\n".join(lines)


@mcp.tool()
def create_board(name: str, columns: list[str] | None = None) -> str:
    """Create a new kanban board.

    Args:
        name: Board name
        columns: Column names (default: backlog, in_progress, done)
    """
    board = storage.create_board(name, columns)
    return f"Created board '{name}' (id: {board['id']})"


@mcp.tool()
def get_board(board_id: str) -> str:
    """Get board details and all items.

    Args:
        board_id: Board ID
    """
    board = storage.get_board(board_id)
    if not board:
        return f"Board '{board_id}' not found."
    lines = [f"Board: {board['name']} (id: {board['id']})"]
    lines.append(f"Columns: {', '.join(board['columns'])}")
    lines.append(f"Items: {len(board['items'])}")
    lines.append("")
    for item in board["items"]:
        sev = item.get("priority", "")
        eff = item.get("effort", "")
        tags = ", ".join(item.get("tags", []))
        meta = f" [{sev}]" if sev and sev != "none" else ""
        meta += f" [{eff}]" if eff else ""
        meta += f" ({tags})" if tags else ""
        lines.append(f"  {item['id']:8s}  {item['status']:14s}  {item['title']}{meta}")
    return "\n".join(lines)


@mcp.tool()
def create_item(
    board_id: str,
    title: str,
    status: str = "backlog",
    description: str = "",
    priority: str = "none",
    effort: str = "",
    tags: list[str] | None = None,
    assignee: str = "",
    due_date: str = "",
) -> str:
    """Create an item on a board.

    Args:
        board_id: Board ID
        title: Item title
        status: Column/status to place it in
        description: Full description
        priority: critical/high/medium/low/none
        effort: XS/S/M/L/XL
        tags: List of tags
        assignee: Assigned person
        due_date: Due date (ISO format)
    """
    item = storage.create_item(
        board_id, title, status,
        description=description, priority=priority, effort=effort,
        tags=tags or [], assignee=assignee, due_date=due_date,
    )
    if not item:
        return f"Board '{board_id}' not found."
    return f"Created item '{item['id']}' in '{status}'"


@mcp.tool()
def update_item(board_id: str, item_id: str, **fields: Any) -> str:
    """Update an item's fields.

    Args:
        board_id: Board ID
        item_id: Item ID
        title: New title
        status: New status/column
        description: New description
        priority: New priority
        effort: New effort estimate
        tags: New tags list
        assignee: New assignee
        due_date: New due date
        sort_order: New sort order
    """
    clean = {k: v for k, v in fields.items() if v is not None and k != "board_id" and k != "item_id"}
    item = storage.update_item(board_id, item_id, **clean)
    if not item:
        return f"Item '{item_id}' not found on board '{board_id}'."
    return f"Updated item '{item_id}'"


@mcp.tool()
def move_item(board_id: str, item_id: str, new_status: str) -> str:
    """Move an item to a different column/status.

    Args:
        board_id: Board ID
        item_id: Item ID
        new_status: Target column name
    """
    item = storage.update_item(board_id, item_id, status=new_status)
    if not item:
        return f"Item '{item_id}' not found on board '{board_id}'."
    return f"Moved '{item_id}' → '{new_status}'"


@mcp.tool()
def delete_item(board_id: str, item_id: str) -> str:
    """Delete an item from a board.

    Args:
        board_id: Board ID
        item_id: Item ID
    """
    if storage.delete_item(board_id, item_id):
        return f"Deleted item '{item_id}'"
    return f"Item '{item_id}' not found on board '{board_id}'."


@mcp.tool()
def search(query: str, board_id: str | None = None) -> str:
    """Search items across all boards or within a specific board.

    Args:
        query: Search query
        board_id: Optional board ID to restrict search
    """
    results = storage.search_items(query, board_id)
    if not results:
        return "No results found."
    lines = []
    for item in results[:20]:
        board_name = item.get("_board_name", item.get("_board", ""))
        lines.append(f"  [{board_name}] {item['id']:8s}  {item['status']:14s}  {item['title']}")
    if len(results) > 20:
        lines.append(f"  ... and {len(results) - 20} more")
    return f"Results ({len(results)}):\n" + "\n".join(lines)


if __name__ == "__main__":
    mcp.run(transport="stdio")
