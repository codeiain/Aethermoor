---
tags:
  - notes
  - markdown
  - ai
---

# NoteDiscovery Service
**Port:** 8800 (host), 8000 (container)  
**Language:** Python 3.12 / FastAPI  
**Data Volume:** `/app/data`

Self-hosted Markdown note-taking app with plugins, graph view, and AI assistant (MCP) integration.

## Responsibilities

- Store and manage Markdown notes in folders
- Provide search, tags, and graph view
- Support plugins for custom features
- Expose REST API for notes, tags, and system info
- Integrate with AI assistants via MCP protocol

## API Endpoints (examples)

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/notes` | List all notes |
| `GET` | `/api/notes/{path}` | Get note content |
| `POST` | `/api/notes` | Create or update a note |
| `DELETE` | `/api/notes/{path}` | Delete a note |
| `GET` | `/api/tags` | List all tags |
| `GET` | `/health` | Liveness probe |

## Notes
- Data is stored in the mapped `/app/data` volume (host: `~/Notes` or similar).
- Authentication and API key support available via environment variables.
