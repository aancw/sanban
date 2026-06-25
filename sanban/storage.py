"""JSON file storage for sanban boards."""
from __future__ import annotations

import json
import os
import time
import uuid
from pathlib import Path
from typing import Any

BOARDS_DIR = Path(os.environ.get("SANBAN_DATA_DIR", Path.home() / ".sanban" / "boards"))


def _board_path(board_id: str) -> Path:
    return BOARDS_DIR / f"{board_id}.json"


def _load(board_id: str) -> dict[str, Any] | None:
    p = _board_path(board_id)
    if not p.exists():
        return None
    return json.loads(p.read_text())


def _save(board_id: str, data: dict) -> None:
    BOARDS_DIR.mkdir(parents=True, exist_ok=True)
    _board_path(board_id).write_text(json.dumps(data, indent=2))


def _gen_id() -> str:
    return uuid.uuid4().hex[:8]


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# ── Boards ──

def list_boards() -> list[dict]:
    BOARDS_DIR.mkdir(parents=True, exist_ok=True)
    boards = []
    for p in sorted(BOARDS_DIR.glob("*.json")):
        try:
            data = json.loads(p.read_text())
            boards.append({
                "id": data["id"],
                "name": data["name"],
                "columns": data.get("columns", []),
                "item_count": len(data.get("items", [])),
            })
        except (json.JSONDecodeError, KeyError):
            continue
    return boards


def create_board(name: str, columns: list[str] | None = None) -> dict:
    board_id = _gen_id()
    data = {
        "id": board_id,
        "name": name,
        "columns": columns or ["backlog", "in_progress", "done"],
        "items": [],
    }
    _save(board_id, data)
    return data


def get_board(board_id: str) -> dict | None:
    return _load(board_id)


def delete_board(board_id: str) -> bool:
    p = _board_path(board_id)
    if p.exists():
        p.unlink()
        return True
    return False


def rename_board(board_id: str, name: str) -> dict | None:
    data = _load(board_id)
    if data is None:
        return None
    data["name"] = name
    _save(board_id, data)
    return data


# ── Items ──

def list_items(board_id: str, status: str | None = None, q: str | None = None,
               tag: str | None = None, assignee: str | None = None) -> list[dict] | None:
    data = _load(board_id)
    if data is None:
        return None
    items = data.get("items", [])
    if status:
        items = [i for i in items if i.get("status") == status]
    if tag:
        items = [i for i in items if tag in i.get("tags", [])]
    if assignee:
        items = [i for i in items if i.get("assignee") == assignee]
    if q:
        q_lower = q.lower()
        items = [i for i in items if q_lower in json.dumps(i).lower()]
    return items


def get_item(board_id: str, item_id: str) -> dict | None:
    data = _load(board_id)
    if data is None:
        return None
    for item in data.get("items", []):
        if item["id"] == item_id:
            return item
    return None


def create_item(board_id: str, title: str, status: str = "backlog", **kwargs) -> dict | None:
    data = _load(board_id)
    if data is None:
        return None
    now = _now()
    item = {
        "id": _gen_id(),
        "title": title,
        "status": status,
        "description": kwargs.get("description", ""),
        "priority": kwargs.get("priority", "none"),
        "effort": kwargs.get("effort", ""),
        "tags": kwargs.get("tags", []),
        "assignee": kwargs.get("assignee", ""),
        "due_date": kwargs.get("due_date", ""),
        "sort_order": kwargs.get("sort_order", 0),
        "created_at": now,
        "updated_at": now,
        "meta": kwargs.get("meta", {}),
    }
    data["items"].append(item)
    _save(board_id, data)
    return item


def update_item(board_id: str, item_id: str, **fields) -> dict | None:
    data = _load(board_id)
    if data is None:
        return None
    for item in data["items"]:
        if item["id"] == item_id:
            for k, v in fields.items():
                if v is not None:
                    item[k] = v
            item["updated_at"] = _now()
            _save(board_id, data)
            return item
    return None


def delete_item(board_id: str, item_id: str) -> bool:
    data = _load(board_id)
    if data is None:
        return False
    before = len(data["items"])
    data["items"] = [i for i in data["items"] if i["id"] != item_id]
    if len(data["items"]) < before:
        _save(board_id, data)
        return True
    return False


def search_items(q: str, board_id: str | None = None) -> list[dict]:
    results = []
    boards = list_boards()
    for b in boards:
        if board_id and b["id"] != board_id:
            continue
        items = list_items(b["id"], q=q) or []
        for item in items:
            item["_board"] = b["id"]
            item["_board_name"] = b["name"]
            results.append(item)
    return results
