# AGENTS.md — Guidance for AI Agents

## Project

sanban is a general-purpose kanban board with REST API + MCP server. JSON file storage, no database. Designed for solo devs and AI agents.

## File Map

| Task | File |
|------|------|
| Storage/CRUD | `sanban/storage.py` |
| REST API | `sanban/rest.py` (FastAPI) |
| MCP tools | `sanban/mcp_server.py` (FastMCP, stdio) |
| Entry point | `sanban/server.py` |
| Frontend | `sanban/static/index.html` |
| Board data | `~/.sanban/boards/<id>.json` |
| JSON schema | `schema.json` |
| Package config | `pyproject.toml` |

## API Base

```
http://localhost:8900/api
```

## Common Tasks

### Create a board

```bash
curl -X POST http://localhost:8900/api/boards \
  -H 'Content-Type: application/json' \
  -d '{"name":"my-board"}'
```

Optional: pass `columns` to customize column names.

```bash
curl -X POST http://localhost:8900/api/boards \
  -H 'Content-Type: application/json' \
  -d '{"name":"my-board","columns":["todo","doing","done"]}'
```

### List boards

```bash
curl http://localhost:8900/api/boards
```

### Get a board with items

```bash
curl http://localhost:8900/api/boards/<board_id>
```

### Delete a board

```bash
curl -X DELETE http://localhost:8900/api/boards/<board_id>
```

### Rename a board

```bash
curl -X PATCH http://localhost:8900/api/boards/<board_id> \
  -H 'Content-Type: application/json' \
  -d '{"name":"new-name"}'
```

### Add an item

```bash
curl -X POST http://localhost:8900/api/boards/<board_id>/items \
  -H 'Content-Type: application/json' \
  -d '{"title":"Fix bug","priority":"high","effort":"S"}'
```

### List items (with filters)

```bash
curl 'http://localhost:8900/api/boards/<board_id>/items?status=in_progress&q=bug&tag=urgent&assignee=alice'
```

### Get a single item

```bash
curl http://localhost:8900/api/boards/<board_id>/items/<item_id>
```

### Move an item

```bash
curl -X PATCH http://localhost:8900/api/boards/<board_id>/items/<item_id> \
  -H 'Content-Type: application/json' \
  -d '{"status":"done"}'
```

### Delete an item

```bash
curl -X DELETE http://localhost:8900/api/boards/<board_id>/items/<item_id>
```

### Search

```bash
curl 'http://localhost:8900/api/search?q=bug'
curl 'http://localhost:8900/api/search?q=bug&board_id=<board_id>'
```

## Item Fields

- `title` — supports **markdown** (bold, code, links, lists)
- `description` — supports **markdown**
- `status` — column name (default: `backlog`, `in_progress`, `done`, `not_applicable`)
- `priority` — `none`, `low`, `medium`, `high`, `critical`
- `effort` — `XS`, `S`, `M`, `L`, `XL`
- `tags` — array of strings
- `assignee` — string
- `due_date` — ISO date string
- `sort_order` — float (default: `0`), controls card ordering within columns
- `meta` — freeform dict for arbitrary metadata
- `created_at` — auto-generated ISO 8601 timestamp
- `updated_at` — auto-updated ISO 8601 timestamp

## MCP Integration

The MCP server exposes tools via stdio transport. Agent config:

```json
{
  "mcpServers": {
    "sanban": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/sanban", "python", "-m", "sanban.server", "--mcp-only"]
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
| `create_item` | `board_id`, `title`, `status?`, `description?`, `priority?`, `effort?`, `tags?`, `assignee?`, `due_date?`, `sort_order?`, `meta?` |
| `get_item` | `board_id`, `item_id` |
| `update_item` | `board_id`, `item_id`, + any field |
| `move_item` | `board_id`, `item_id`, `new_status` |
| `delete_item` | `board_id`, `item_id` |
| `search` | `query`, `board_id?` |

## Server CLI

```
python -m sanban.server [--host HOST] [--port PORT] [--mcp-only] [--rest-only]
```

| Flag | Default | Description |
|------|---------|-------------|
| `--host` | `0.0.0.0` | Bind address |
| `--port` | `8900` | Listen port |
| `--mcp-only` | false | Run MCP server only (no REST/UI) |
| `--rest-only` | false | Run REST server only (no MCP) |

## Frontend

Single-file vanilla HTML/CSS/JS at `sanban/static/index.html`. No build step, no framework.

- **Welcome screen**: When no boards exist, a centered card prompts the user to create their first board. Header and board grid are hidden until a board is created.
- **Board creation**: Uses a custom modal (not browser `prompt()`). The `+ board` button opens the modal; the welcome form also triggers board creation.
- **Item creation/editing**: Modal overlay with form fields (title, description, status, priority, effort, tags, assignee, due date). Includes markdown preview toggle for description.
- **Board management**: Delete board and rename board buttons in header.
- **Overdue highlighting**: Cards with past due dates show red badge (unless in done column).
- **Drag & drop**: Native HTML5 drag-and-drop for moving cards between columns.
- **Keyboard shortcuts**: `/` search, `n` new item, `e` expand/collapse all, `Esc` close modals.
- **Styling**: Dark theme via CSS custom properties, Geist font family, `prefers-reduced-motion` respected.

## Conventions

- Board IDs and item IDs are auto-generated 8-char hex
- Timestamps are ISO 8601 UTC
- Board columns are customizable (default: backlog, in_progress, done, not_applicable)
- JSON files are the source of truth — edit directly or via API
- Frontend uses `localStorage` for drag state; API is source of truth
