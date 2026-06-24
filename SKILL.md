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
sanban
# Open http://localhost:8900
```

## REST API

Base: `http://localhost:8900/api`

```
GET    /api/boards                  — list boards
POST   /api/boards                  — create board { name, columns? }
GET    /api/boards/:id              — get board + items
DELETE /api/boards/:id              — delete board
GET    /api/boards/:id/items        — list items (?q=, ?status=, ?tag=, ?assignee=)
POST   /api/boards/:id/items        — create item
PATCH  /api/boards/:id/items/:iid   — update item
DELETE /api/boards/:id/items/:iid   — delete item
GET    /api/search?q=               — search across boards
```

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

## MCP Tools

| Tool | Args |
|------|------|
| `list_boards` | — |
| `create_board` | `name`, `columns?` |
| `get_board` | `board_id` |
| `create_item` | `board_id`, `title`, `status?`, `priority?`, `effort?`, `tags?`, `assignee?`, `due_date?`, `description?` |
| `update_item` | `board_id`, `item_id`, + any field |
| `move_item` | `board_id`, `item_id`, `new_status` |
| `delete_item` | `board_id`, `item_id` |
| `search` | `query`, `board_id?` |

## Agent Config (MCP)

```json
{
  "mcpServers": {
    "sanban": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/sanban", "python", "-m", "sanban.server"]
    }
  }
}
```

## Data Location

`~/.sanban/boards/<id>.json` — one JSON file per board. Override with `SANBAN_DATA_DIR`.

## Markdown Support

Titles and descriptions render markdown: `**bold**`, `*italic*`, `` `code` ``, `[links](url)`, `- lists`, `# headings`.

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `/` | Focus search |
| `n` | New item |
| `e` | Expand/collapse all cards |
| `Esc` | Close modal / clear search |
