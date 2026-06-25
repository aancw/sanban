"""FastAPI REST API for sanban."""
from __future__ import annotations

import csv
import io
import json
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from pathlib import Path

from sanban import storage

app = FastAPI(title="sanban", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request models ──

class BoardCreate(BaseModel):
    name: str
    columns: list[str] | None = None


class BoardRename(BaseModel):
    name: str | None = None
    columns: list[str] | None = None


class ItemCreate(BaseModel):
    title: str
    status: str = "backlog"
    description: str = ""
    priority: str = "none"
    effort: str = ""
    tags: list[str] = []
    assignee: str = ""
    due_date: str = ""
    sort_order: float = 0
    meta: dict[str, Any] = {}


class ItemUpdate(BaseModel):
    title: str | None = None
    status: str | None = None
    description: str | None = None
    priority: str | None = None
    effort: str | None = None
    tags: list[str] | None = None
    assignee: str | None = None
    due_date: str | None = None
    sort_order: float | None = None
    meta: dict[str, Any] | None = None
    subtasks: list[dict[str, Any]] | None = None
    dependencies: list[str] | None = None


class BoardDuplicate(BaseModel):
    name: str | None = None


class ImportData(BaseModel):
    name: str | None = None
    columns: list[str] | None = None
    items: list[dict[str, Any]] | None = None


# ── Board endpoints ──

@app.get("/api/boards")
def api_list_boards():
    return storage.list_boards()


@app.post("/api/boards", status_code=201)
def api_create_board(body: BoardCreate):
    return storage.create_board(body.name, body.columns)


@app.get("/api/boards/{board_id}")
def api_get_board(board_id: str):
    board = storage.get_board(board_id)
    if not board:
        raise HTTPException(404, "Board not found")
    return board


@app.delete("/api/boards/{board_id}")
def api_delete_board(board_id: str):
    if not storage.delete_board(board_id):
        raise HTTPException(404, "Board not found")
    return {"ok": True}


@app.patch("/api/boards/{board_id}")
def api_rename_board(board_id: str, body: BoardRename):
    board = storage.get_board(board_id)
    if not board:
        raise HTTPException(404, "Board not found")
    if body.name is not None:
        board = storage.rename_board(board_id, body.name)
    if body.columns is not None:
        board = storage.update_board_columns(board_id, body.columns)
    return board


# ── Item endpoints ──

@app.get("/api/boards/{board_id}/items")
def api_list_items(
    board_id: str,
    status: str | None = None,
    q: str | None = None,
    tag: str | None = None,
    assignee: str | None = None,
):
    items = storage.list_items(board_id, status=status, q=q, tag=tag, assignee=assignee)
    if items is None:
        raise HTTPException(404, "Board not found")
    return items


@app.get("/api/boards/{board_id}/items/{item_id}")
def api_get_item(board_id: str, item_id: str):
    item = storage.get_item(board_id, item_id)
    if not item:
        raise HTTPException(404, "Item or board not found")
    return item


@app.post("/api/boards/{board_id}/items", status_code=201)
def api_create_item(board_id: str, body: ItemCreate):
    item = storage.create_item(board_id, body.title, body.status, **body.model_dump(exclude={"title", "status"}))
    if not item:
        raise HTTPException(404, "Board not found")
    return item


@app.patch("/api/boards/{board_id}/items/{item_id}")
def api_update_item(board_id: str, item_id: str, body: ItemUpdate):
    fields = {k: v for k, v in body.model_dump().items() if v is not None}
    item = storage.update_item(board_id, item_id, **fields)
    if not item:
        raise HTTPException(404, "Item or board not found")
    return item


@app.delete("/api/boards/{board_id}/items/{item_id}")
def api_delete_item(board_id: str, item_id: str):
    if not storage.delete_item(board_id, item_id):
        raise HTTPException(404, "Item or board not found")
    return {"ok": True}


# ── History ──

@app.get("/api/boards/{board_id}/history")
def api_get_history(board_id: str, limit: int = Query(50, ge=1, le=500)):
    board = storage.get_board(board_id)
    if not board:
        raise HTTPException(404, "Board not found")
    return storage.get_history(board_id, limit)


# ── Board Duplication ──

@app.post("/api/boards/{board_id}/duplicate", status_code=201)
def api_duplicate_board(board_id: str, body: BoardDuplicate):
    new_board = storage.duplicate_board(board_id, body.name)
    if not new_board:
        raise HTTPException(404, "Board not found")
    return new_board


# ── Export / Import ──

@app.get("/api/boards/{board_id}/export")
def api_export_board(board_id: str, format: str = Query("json")):
    board = storage.get_board(board_id)
    if not board:
        raise HTTPException(404, "Board not found")
    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "title", "status", "priority", "effort", "tags",
                         "assignee", "due_date", "description", "sort_order",
                         "created_at", "updated_at", "meta", "subtasks", "dependencies"])
        for item in board.get("items", []):
            writer.writerow([
                item.get("id", ""), item.get("title", ""), item.get("status", ""),
                item.get("priority", ""), item.get("effort", ""),
                json.dumps(item.get("tags", [])), item.get("assignee", ""),
                item.get("due_date", ""), item.get("description", ""),
                item.get("sort_order", 0), item.get("created_at", ""),
                item.get("updated_at", ""), json.dumps(item.get("meta", {})),
                json.dumps(item.get("subtasks", [])),
                json.dumps(item.get("dependencies", [])),
            ])
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={board['name']}.csv"},
        )
    return board


@app.post("/api/import", status_code=201)
def api_import_board(body: ImportData):
    name = body.name or "imported-board"
    columns = body.columns or ["backlog", "in_progress", "done"]
    board = storage.create_board(name, columns)
    if body.items:
        for item_data in body.items:
            storage.create_item(
                board["id"],
                item_data.get("title", "Untitled"),
                status=item_data.get("status", columns[0]),
                description=item_data.get("description", ""),
                priority=item_data.get("priority", "none"),
                effort=item_data.get("effort", ""),
                tags=item_data.get("tags", []),
                assignee=item_data.get("assignee", ""),
                due_date=item_data.get("due_date", ""),
                sort_order=item_data.get("sort_order", 0),
                meta=item_data.get("meta", {}),
                subtasks=item_data.get("subtasks", []),
                dependencies=item_data.get("dependencies", []),
            )
    return storage.get_board(board["id"])


# ── Search ──

@app.get("/api/search")
def api_search(q: str, board_id: str | None = None):
    return storage.search_items(q, board_id)


# ── Static files (serve frontend) ──

static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
