"""FastAPI REST API for sanban."""
from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
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


# ── Search ──

@app.get("/api/search")
def api_search(q: str, board_id: str | None = None):
    return storage.search_items(q, board_id)


# ── Static files (serve frontend) ──

static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
