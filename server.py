from mcp.server.fastmcp import FastMCP

from tools.file_tools import tool_load_ifc_file, tool_list_loaded_models, tool_unload_ifc_file
from tools.spatial_tools import tool_get_spatial_structure, tool_get_element_containment
from tools.element_tools import tool_get_elements_by_type, tool_get_element_by_id, tool_search_elements
from tools.property_tools import tool_get_property_sets, tool_get_quantities, tool_get_material
from tools.geometry_tools import tool_get_model_statistics, tool_get_bounding_box
from resources.model_summary import get_summary

mcp = FastMCP("ifc-mcp")


@mcp.tool()
def load_ifc_file(path: str) -> dict:
    """Load an IFC file from the given path. Returns model_id for subsequent queries."""
    return tool_load_ifc_file(path)


@mcp.tool()
def list_loaded_models() -> list:
    """List all IFC models currently loaded in memory."""
    return tool_list_loaded_models()


@mcp.tool()
def unload_ifc_file(model_id: str) -> dict:
    """Unload an IFC model from memory to free resources."""
    return tool_unload_ifc_file(model_id)


@mcp.tool()
def get_spatial_structure(model_id: str) -> dict:
    """Get the full spatial hierarchy: Project > Site > Building > Storey > Space."""
    return tool_get_spatial_structure(model_id)


@mcp.tool()
def get_element_containment(model_id: str, global_id: str) -> dict:
    """Get which storey/building/site contains the given element."""
    return tool_get_element_containment(model_id, global_id)


@mcp.tool()
def get_elements_by_type(model_id: str, ifc_type: str, limit: int = 100, offset: int = 0) -> dict:
    """Get elements of a given IFC type (e.g. IfcWall, IfcDoor). Supports pagination via limit/offset."""
    return tool_get_elements_by_type(model_id, ifc_type, limit, offset)


@mcp.tool()
def get_element_by_id(model_id: str, global_id: str) -> dict:
    """Get full details for a single element by its GlobalId."""
    return tool_get_element_by_id(model_id, global_id)


@mcp.tool()
def search_elements(
    model_id: str,
    ifc_type: str | None = None,
    name_contains: str | None = None,
    pset_name: str | None = None,
    property_name: str | None = None,
    property_value: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict:
    """Search elements with optional filters: IFC type, name substring, property set name/value."""
    return tool_search_elements(
        model_id, ifc_type, name_contains, pset_name, property_name, property_value, limit, offset
    )


@mcp.tool()
def get_property_sets(model_id: str, global_id: str) -> dict:
    """Get all property sets (Psets) for an element as {pset_name: {prop_name: value}}."""
    return tool_get_property_sets(model_id, global_id)


@mcp.tool()
def get_quantities(model_id: str, global_id: str) -> dict:
    """Get all quantity sets for an element as {qset_name: {quantity_name: value}}."""
    return tool_get_quantities(model_id, global_id)


@mcp.tool()
def get_material(model_id: str, global_id: str) -> dict:
    """Get material information for an element."""
    return tool_get_material(model_id, global_id)


@mcp.tool()
def get_model_statistics(model_id: str) -> dict:
    """Get element counts by IFC type, storey names, schema version, and total count."""
    return tool_get_model_statistics(model_id)


@mcp.tool()
def get_bounding_box(model_id: str, global_id: str) -> dict:
    """Get the bounding box (min/max XYZ and dimensions) of an element in project coordinates."""
    return tool_get_bounding_box(model_id, global_id)


@mcp.resource("ifc://model/{model_id}/summary")
def model_summary_resource(model_id: str) -> str:
    """Pre-computed text summary of the IFC model, suitable for AI context injection."""
    return get_summary(model_id)


if __name__ == "__main__":
    mcp.run()
