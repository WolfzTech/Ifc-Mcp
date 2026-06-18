# IFC MCP Server

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server that enables AI agents to understand and query IFC (Industry Foundation Classes) building model files. This server exposes a rich set of tools for loading IFC files, traversing spatial hierarchies, inspecting elements and properties, querying materials and quantities, and retrieving geometry bounding boxes — allowing AI assistants like Claude to reason about building information models without requiring the user to manually extract data.

---

## Installation

### From PyPI (recommended)

```bash
pip install ifc-mcp
# or with uv:
uv tool install ifc-mcp
```

Claude Desktop config (no path needed):
```json
{
  "mcpServers": {
    "ifc": {
      "command": "uvx",
      "args": ["ifc-mcp"]
    }
  }
}
```

### To update

```bash
uv tool upgrade ifc-mcp
```

Or pin to a specific version:
```json
"args": ["ifc-mcp==0.2.0"]
```

### Skip permission prompts (Claude Code)

Add the tools to your `~/.claude/settings.json` so Claude Code never asks for confirmation:

```json
{
  "permissions": {
    "allow": [
      "mcp__ifc__load_ifc_file",
      "mcp__ifc__list_loaded_models",
      "mcp__ifc__unload_ifc_file",
      "mcp__ifc__get_spatial_structure",
      "mcp__ifc__get_element_containment",
      "mcp__ifc__get_elements_by_type",
      "mcp__ifc__get_element_by_id",
      "mcp__ifc__search_elements",
      "mcp__ifc__get_property_sets",
      "mcp__ifc__get_quantities",
      "mcp__ifc__get_material",
      "mcp__ifc__get_model_statistics",
      "mcp__ifc__get_bounding_box",
      "mcp__ifc__get_element_placement",
      "mcp__ifc__get_element_local_bbox",
      "mcp__ifc__get_element_body_mapping",
      "mcp__ifc__get_property_sets_detail",
      "mcp__ifc__get_element_by_label",
      "mcp__ifc__get_representation",
      "mcp__ifc__get_elements_batch"
    ]
  }
}
```

---

## Development Setup

Prerequisites: Python 3.11+, [uv](https://docs.astral.sh/uv/)

```bash
git clone <repo>
cd IfcMcp
uv sync
uv run pytest                            # verify all tests pass
```

Claude Desktop config for local dev:
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
| `get_element_containment` | `model_id`, `global_id` | Full containment chain up to Site |
| `get_elements_by_type` | `model_id`, `ifc_type`, `limit`, `offset` | Paginated list by IFC type |
| `get_element_by_id` | `model_id`, `global_id` | Full element details (includes `entity_label`, `type_global_id`) |
| `get_element_by_label` | `model_id`, `entity_label` | Look up element by integer STEP label (`#NNN`) |
| `get_elements_batch` | `model_id`, `global_ids`, `include` | Batch query; `include`: `entity_label`, `placement`, `property_sets`, `local_bbox` |
| `search_elements` | `model_id`, filters..., `limit`, `offset` | Filter elements by type/name/pset/property |
| `get_property_sets` | `model_id`, `global_id` | All Psets for an element |
| `get_property_sets_detail` | `model_id`, `global_id` | Psets split by instance-level vs type-level |
| `get_quantities` | `model_id`, `global_id` | All quantity sets for an element |
| `get_material` | `model_id`, `global_id` | Material info (name, layers, category) |
| `get_model_statistics` | `model_id` | Element counts by type, storey names, schema |
| `get_bounding_box` | `model_id`, `global_id` | Min/max XYZ bounding box in world coordinates |
| `get_element_placement` | `model_id`, `global_id` | `object_placement` + `world_transform` + determinant + body mapping flag |
| `get_element_local_bbox` | `model_id`, `global_id` | Bounding box in element's local coordinate frame |
| `get_element_body_mapping` | `model_id`, `global_id` | Body mapping matrix, world transform, mirroring detection |
| `get_representation` | `model_id`, `global_id` | Representation structure without tessellating geometry |

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
