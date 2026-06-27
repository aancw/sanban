---
name: sanban
description: Simple kanban that just works. JSON-backed boards with REST API + MCP server.
---

# Skill: sanban

Simple kanban that just works. JSON-backed boards with REST API + MCP server.

## When to Use

- User wants to track tasks, issues, or work items
- Agent needs to create/update/list kanban items programmatically
- User asks for a lightweight project tracker (no Jira/Linear/Notion)
- Multi-board project management from CLI or browser

## Quick Start

```bash
uv tool install .
sanban              # web server on http://localhost:8900
```

## Connection Method: REST API

Use when: running in browser, curl available, or agent prefers HTTP requests.

### Setup

```bash
sanban              # starts REST server on http://localhost:8900
```

### Base URL

```
http://localhost:8900/api
```

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/boards` | List boards |
| `POST` | `/api/boards` | Create board `{ name, columns? }` |
| `GET` | `/api/boards/:id` | Get board + items |
| `PATCH` | `/api/boards/:id` | Rename board / update columns `{ name?, columns? }` |
| `DELETE` | `/api/boards/:id` | Delete board |
| `POST` | `/api/boards/:id/duplicate` | Duplicate board `{ name? }` |
| `GET` | `/api/boards/:id/items` | List items (`?q=`, `?status=`, `?tag=`, `?assignee=`) |
| `POST` | `/api/boards/:id/items` | Create item |
| `GET` | `/api/boards/:id/items/:iid` | Get single item |
| `PATCH` | `/api/boards/:id/items/:iid` | Update item (any field) |
| `DELETE` | `/api/boards/:id/items/:iid` | Delete item |
| `GET` | `/api/boards/:id/history?limit=` | Activity history (`limit` 1–500, default 50) |
| `GET` | `/api/boards/:id/export?format=json\|csv` | Export board |
| `POST` | `/api/import` | Import board `{ name?, columns?, items[] }` |
| `GET` | `/api/search?q=&board_id=` | Search across boards |

### Examples

**Create board:**
```bash
curl -X POST http://localhost:8900/api/boards \
  -H 'Content-Type: application/json' \
  -d '{"name":"my-board"}'
```

**Rename / update columns:**
```bash
curl -X PATCH http://localhost:8900/api/boards/<board_id> \
  -H 'Content-Type: application/json' \
  -d '{"name":"new-name","columns":["todo","doing","done"]}'
```

**Duplicate board:**
```bash
curl -X POST http://localhost:8900/api/boards/<board_id>/duplicate \
  -H 'Content-Type: application/json' \
  -d '{"name":"copy-of-board"}'
```

**Add item:**
```bash
curl -X POST http://localhost:8900/api/boards/<board_id>/items \
  -H 'Content-Type: application/json' \
  -d '{"title":"Fix bug","priority":"high","effort":"S"}'
```

**Move item:**
```bash
curl -X PATCH http://localhost:8900/api/boards/<board_id>/items/<item_id> \
  -H 'Content-Type: application/json' \
  -d '{"status":"done"}'
```

**Export board as CSV:**
```bash
curl 'http://localhost:8900/api/boards/<board_id>/export?format=csv' -o board.csv
```

**Import board:**
```bash
curl -X POST http://localhost:8900/api/import \
  -H 'Content-Type: application/json' \
  -d '{"name":"imported","columns":["todo","done"],"items":[{"title":"One","status":"todo"}]}'
```

**Activity history:**
```bash
curl 'http://localhost:8900/api/boards/<board_id>/history?limit=20'
```

---

## Connection Method: MCP

Use when: agent has MCP tools available, prefer direct tool calls over HTTP.

### Setup

```json
{
  "mcpServers": {
    "sanban": {
      "command": "sanban",
      "args": ["--mcp-only"]
    }
  }
}
```

### MCP Tools

| Tool | Args |
|------|------|
| `list_boards` | — |
| `create_board` | `name`, `columns?` |
| `get_board` | `board_id` |
| `delete_board` | `board_id` |
| `duplicate_board` | `board_id`, `name?` |
| `get_item` | `board_id`, `item_id` |
| `create_item` | `board_id`, `title`, `status?`, `description?`, `priority?`, `effort?`, `tags?`, `assignee?`, `due_date?`, `sort_order?`, `meta?` |
| `update_item` | `board_id`, `item_id`, + any field |
| `move_item` | `board_id`, `item_id`, `new_status` |
| `delete_item` | `board_id`, `item_id` |
| `search` | `query`, `board_id?` |
| `get_history` | `board_id`, `limit?` (default 50) |

---

## Item Fields

| Field | Values | Default |
|-------|--------|---------|
| title | string (markdown) | required |
| status | column name | `backlog` |
| priority | `none` `low` `medium` `high` `critical` | `none` |
| effort | `XS` `S` `M` `L` `XL` | empty |
| tags | string[] | `[]` |
| assignee | string | empty |
| due_date | ISO date | empty |
| description | string (markdown) | empty |
| sort_order | float (lower = higher in column) | `0` |
| meta | freeform dict | `{}` |
| subtasks | list of `{ id, title, done? }` | `[]` |
| dependencies | list of item IDs | `[]` |

## Data Location

`~/.sanban/boards/<id>.json` — one JSON file per board. Activity log: `~/.sanban/history/<id>.json` (capped at 500 entries). Override both with `SANBAN_DATA_DIR`.

## Markdown Support

Titles and descriptions render markdown: `**bold**`, `*italic*`, `` `code` ``, `[links](url)`, `- lists`, `# headings`.

## Keyboard Shortcuts (Web UI)

| Key | Action |
|-----|--------|
| `/` | Focus search |
| `n` | New item |
| `e` | Expand/collapse all cards |
| `Esc` | Close modal / clear search |

## Server CLI

```
sanban [--host HOST] [--port PORT] [--mcp-only] [--rest-only]
```

| Flag | Default | Description |
|------|---------|-------------|
| `--host` | `0.0.0.0` | Bind address |
| `--port` | `8900` | Listen port |
| `--mcp-only` | false | Run MCP server only (no REST/UI) |
| `--rest-only` | false | Run REST server only (no MCP) |
