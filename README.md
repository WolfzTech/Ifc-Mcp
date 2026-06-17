# IFC MCP Server

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server that enables AI agents to understand and query IFC (Industry Foundation Classes) building model files. This server exposes a rich set of tools for loading IFC files, traversing spatial hierarchies, inspecting elements and properties, querying materials and quantities, and retrieving geometry bounding boxes — allowing AI assistants like Claude to reason about building information models without requiring the user to manually extract data.

---

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (fast Python package manager)

---

## Setup

```bash
git clone <repo>
cd IfcMcp
uv sync
uv run python tests/create_fixture.py   # only needed if you delete the committed fixture
uv run pytest                            # verify all tests pass
```

---

## Running the Server

```bash
uv run python server.py
```

---

## Claude Desktop Config

Paste the following into your `claude_desktop_config.json` file (replace `/absolute/path/to/IfcMcp` with the actual path on your machine):

```json
{
  "mcpServers": {
    "ifc": {
      "command": "uv",
      "args": ["run", "python", "server.py"],
      "cwd": "/absolute/path/to/IfcMcp"
    }
  }
}
```

On Windows, use double backslashes: `"cwd": "C:\\Users\\...\\IfcMcp"`

---

## Tools Reference

Every tool (except `list_loaded_models`) requires a `model_id` — the value returned by `load_ifc_file`.

| Tool | Parameters | Description |
|------|-----------|-------------|
| `load_ifc_file` | `path` | Load an IFC file; returns `model_id` |
| `list_loaded_models` | — | List all models in memory |
| `unload_ifc_file` | `model_id` | Free a loaded model |
| `get_spatial_structure` | `model_id` | Full spatial hierarchy (Project→Site→Building→Storey→Space) |
| `get_element_containment` | `model_id`, `global_id` | Spatial containment chain for an element |
| `get_elements_by_type` | `model_id`, `ifc_type`, `limit`, `offset` | Paginated list by IFC type |
| `get_element_by_id` | `model_id`, `global_id` | Full element details |
| `search_elements` | `model_id`, filters..., `limit`, `offset` | Filter elements by type/name/pset/property |
| `get_property_sets` | `model_id`, `global_id` | All Psets for an element |
| `get_quantities` | `model_id`, `global_id` | All quantity sets for an element |
| `get_material` | `model_id`, `global_id` | Material info (name, layers, category) |
| `get_model_statistics` | `model_id` | Element counts by type, storey names, schema |
| `get_bounding_box` | `model_id`, `global_id` | Min/max XYZ bounding box in project coordinates |

---

## MCP Resource

Each loaded model exposes a pre-computed summary resource:

```
ifc://model/{model_id}/summary
```

This resource is computed at load time and contains the project name, IFC schema version, element counts by type, and storey names. It gives AI agents a fast overview of a model without issuing individual tool calls.

---

## Error Responses

All tools return structured error objects. Common codes:

```json
{"error": "element_not_found", "details": "..."}
{"error": "model_not_loaded", "details": "..."}
{"error": "geometry_unavailable", "details": "..."}
{"error": "file_not_found", "details": "..."}
{"error": "load_failed", "details": "..."}
{"error": "query_failed", "details": "..."}
```
