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
| Frontend | `static/index.html` |
| Board data | `~/.sanban/boards/<id>.json` |

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

### Add an item

```bash
curl -X POST http://localhost:8900/api/boards/<board_id>/items \
  -H 'Content-Type: application/json' \
  -d '{"title":"Fix bug","priority":"high","effort":"S"}'
```

### Move an item

```bash
curl -X PATCH http://localhost:8900/api/boards/<board_id>/items/<item_id> \
  -H 'Content-Type: application/json' \
  -d '{"status":"done"}'
```

### Search

```bash
curl 'http://localhost:8900/api/search?q=bug'
```

## Item Fields

- `title` — supports **markdown** (bold, code, links, lists)
- `description` — supports **markdown**
- `status` — column name (default: `backlog`, `in_progress`, `done`)
- `priority` — `none`, `low`, `medium`, `high`, `critical`
- `effort` — `XS`, `S`, `M`, `L`, `XL`
- `tags` — array of strings
- `assignee` — string
- `due_date` — ISO date string

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

## Frontend

Single-file vanilla HTML/CSS/JS at `static/index.html`. No build step, no framework.

- **Welcome screen**: When no boards exist, a centered card prompts the user to create their first board. Header and board grid are hidden until a board is created.
- **Board creation**: Uses a custom modal (not browser `prompt()`). The `+ board` button opens the modal; the welcome form also triggers board creation.
- **Item creation/editing**: Modal overlay with form fields (title, description, status, priority, effort, tags, assignee, due date).
- **Drag & drop**: Native HTML5 drag-and-drop for moving cards between columns.
- **Keyboard shortcuts**: `/` search, `n` new item, `e` expand/collapse all, `Esc` close modals.
- **Styling**: Dark theme via CSS custom properties, Geist font family, `prefers-reduced-motion` respected.

## Conventions

- Board IDs and item IDs are auto-generated 8-char hex
- Timestamps are ISO 8601 UTC
- Board columns are customizable (default: backlog, in_progress, done)
- JSON files are the source of truth — edit directly or via API
- Frontend uses `localStorage` for drag state; API is source of truth
