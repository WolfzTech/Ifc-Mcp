# IFC MCP Server — Design Spec

**Date:** 2026-06-16  
**Status:** Approved  
**Stack:** Python + IfcOpenShell + MCP SDK

---

## Overview

An MCP server that gives AI agents full BIM comprehension of IFC files. The agent can load IFC models, navigate the spatial hierarchy, query elements, read property sets and quantities, inspect geometry, and receive a pre-loaded model summary as an MCP resource. Designed local-first with clean extension points for remote/cloud deployment.

---

## Architecture

```
IfcMcp/
├── src/
│   ├── server.py            — MCP server entry point & tool registration
│   ├── ifc_manager.py       — in-memory registry of loaded IFC models
│   ├── tools/
│   │   ├── file_tools.py    — load / unload / list models
│   │   ├── spatial_tools.py — spatial hierarchy and containment queries
│   │   ├── element_tools.py — query elements by type, GlobalId, or filters
│   │   ├── property_tools.py — Psets, quantity sets, materials, classifications
│   │   └── geometry_tools.py — bounding boxes, areas, volumes
│   └── resources/
│       └── model_summary.py — MCP resource: model overview for context injection
├── tests/
│   └── fixtures/            — small IFC fixture file (2-storey building)
├── pyproject.toml
└── README.md
```

**Runtime:** Python 3.11+, managed with `uv`.  
**IFC engine:** IfcOpenShell (C++ bindings via wheel).  
**MCP SDK:** `mcp` (Anthropic's Python MCP SDK).

---

## Session-Based Model Registry

`ifc_manager.py` maintains a process-lifetime dict:

```
{ model_id: ifcopenshell.file }
```

`model_id` is derived from the file's basename + a short content hash to avoid collisions. The registry lives only for the server's lifetime — no persistence. If the server restarts, files must be re-loaded. This keeps the server stateless and dependency-free.

---

## MCP Tools

### File Management

| Tool | Parameters | Returns |
|------|-----------|---------|
| `load_ifc_file` | `path: str` | `{ model_id, project_name, schema, element_count }` |
| `list_loaded_models` | — | list of `{ model_id, path, element_count }` |
| `unload_ifc_file` | `model_id: str` | `{ success: bool }` |

### Spatial Structure

| Tool | Parameters | Returns |
|------|-----------|---------|
| `get_spatial_structure` | `model_id` | nested JSON: Project → Site → Building → Storey → Space |
| `get_element_containment` | `model_id`, `global_id` | `{ storey, building, site, space? }` |

### Element Queries

| Tool | Parameters | Returns |
|------|-----------|---------|
| `get_elements_by_type` | `model_id`, `ifc_type`, `limit=100`, `offset=0` | list of `{ global_id, name, type, description }` |
| `get_element_by_id` | `model_id`, `global_id` | full element dict including type, name, all direct attributes |
| `search_elements` | `model_id`, `ifc_type?`, `name_contains?`, `pset_name?`, `property_name?`, `property_value?`, `limit=100`, `offset=0` | filtered list |

### Properties & Materials

| Tool | Parameters | Returns |
|------|-----------|---------|
| `get_property_sets` | `model_id`, `global_id` | `{ pset_name: { prop_name: value } }` |
| `get_quantities` | `model_id`, `global_id` | `{ qset_name: { quantity_name: { value, unit } } }` |
| `get_material` | `model_id`, `global_id` | `{ name, layers?: [{ name, thickness }], category? }` |

### Geometry

| Tool | Parameters | Returns |
|------|-----------|---------|
| `get_bounding_box` | `model_id`, `global_id` | `{ min: {x,y,z}, max: {x,y,z}, dimensions: {width,depth,height} }` |
| `get_model_statistics` | `model_id` | element counts by IFC type, storey count, schema version |

---

## MCP Resource

`ifc://model/{model_id}/summary`

Pre-computed on `load_ifc_file`. Contains:
- Project name, schema version (IFC2x3 / IFC4 / IFC4x3)
- Element counts by top IFC type (IfcWall: 142, IfcDoor: 38, …)
- Storey names and levels
- Disciplines detected (structural, architectural, MEP)

Registered as an MCP resource so agents can reference it for automatic context injection without an explicit tool call.

---

## Data Flow

1. Agent calls `load_ifc_file(path)` → IfcOpenShell parses file → `ifc_manager` stores the `ifcopenshell.file` object → model summary pre-computed → `model_id` returned
2. All subsequent tool calls pass `model_id` → manager returns the in-memory object → no re-parsing
3. Geometry (`get_bounding_box`) is computed lazily via `ifcopenshell.geom.create_shape()` only on demand
4. `get_elements_by_type` and `search_elements` are paginated (`limit` + `offset`) to prevent flooding the agent with thousands of results

---

## Error Handling

All tools return structured dicts — never raw exceptions:

```json
{ "error": "element_not_found", "details": "No element with GlobalId 'abc123'" }
{ "error": "model_not_loaded", "details": "Call load_ifc_file first" }
{ "error": "geometry_unavailable", "details": "Element has no geometry representation" }
{ "error": "file_not_found", "details": "Path 'C:/foo.ifc' does not exist" }
```

The agent can inspect `error` and reason about the failure without crashing.

---

## Testing

- Unit tests per tool module in `tests/`, using a small IFC fixture committed to `tests/fixtures/sample.ifc`
- One integration test per tool that loads the fixture and asserts the shape of the JSON response
- No mocking of IfcOpenShell — tests run against the real library and the real fixture file
- Test runner: `pytest`

---

## Local Setup & MCP Config

```bash
uv sync
uv run mcp dev src/server.py          # interactive dev mode
uv run python -m src.server           # production stdio mode
```

Claude Desktop `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "ifc": {
      "command": "uv",
      "args": ["run", "python", "-m", "src.server"],
      "cwd": "/path/to/IfcMcp"
    }
  }
}
```

---

## Future Extensions (out of scope for v1)

- Remote file loading from URLs / S3 (add `load_ifc_url` tool)
- Persistent model cache across server restarts (SQLite or file-based)
- IFC writing / modification tools
- Clash detection queries
