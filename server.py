"""IFC MCP server — registers all tools and the model summary resource."""

from mcp.server.fastmcp import FastMCP

from tools.file_tools import tool_load_ifc_file, tool_list_loaded_models, tool_unload_ifc_file
from tools.spatial_tools import tool_get_spatial_structure, tool_get_element_containment
from tools.element_tools import tool_get_elements_by_type, tool_get_element_by_id, tool_search_elements, tool_get_element_by_label, tool_get_elements_batch
from tools.property_tools import tool_get_property_sets, tool_get_quantities, tool_get_material, tool_get_property_sets_detail
from tools.geometry_tools import tool_get_model_statistics, tool_get_bounding_box, tool_get_element_placement, tool_get_element_local_bbox, tool_get_element_body_mapping, tool_get_representation
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
    """Get the spatial containment chain for an element (Space > Storey > Building > Site)."""
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
    """Search elements with optional filters: IFC type, name substring, pset_name (must own this pset), property_name/property_value (property within that pset or any pset). Supports pagination via limit/offset."""
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
    """Get material information for an element. Returns {name, layers, category} — layers is a list of {name, thickness} for layered assemblies, or None for simple materials."""
    return tool_get_material(model_id, global_id)


@mcp.tool()
def get_model_statistics(model_id: str) -> dict:
    """Get element counts by IFC type, storey names, schema version, and total count."""
    return tool_get_model_statistics(model_id)


@mcp.tool()
def get_bounding_box(model_id: str, global_id: str) -> dict:
    """Get the bounding box (min/max XYZ and dimensions) of an element in project coordinates."""
    return tool_get_bounding_box(model_id, global_id)


@mcp.tool()
def get_element_placement(model_id: str, global_id: str) -> dict:
    """Get the world-space placement of an element: insertion point (XYZ) and orientation axes (X/Y/Z unit vectors). Useful for position, rotation, and aim direction of elements like luminaires."""
    return tool_get_element_placement(model_id, global_id)


@mcp.tool()
def get_element_local_bbox(model_id: str, global_id: str) -> dict:
    """Get the local-space bounding box of an element (no world transform applied). Returns min/max XYZ and dimensions in the element's own coordinate system. Use for mounting axis prediction and recessed fixture detection."""
    return tool_get_element_local_bbox(model_id, global_id)


@mcp.tool()
def get_element_body_mapping(model_id: str, global_id: str) -> dict:
    """Get the body mapping matrix for an element with IfcMappedItem geometry. Returns: has_mapped_item, body_mapping_matrix (4x4), world_transform (OPM × body mapping), world_transform_determinant, is_mirrored (det<0 means Y-negation needed). Essential for detecting baked rotations in luminaire imports."""
    return tool_get_element_body_mapping(model_id, global_id)


@mcp.tool()
def get_property_sets_detail(model_id: str, global_id: str) -> dict:
    """Get property sets split by source: instance-level psets vs type-level psets. Use to determine whether a property was overridden at instance level or inherited from the type."""
    return tool_get_property_sets_detail(model_id, global_id)


@mcp.tool()
def get_element_by_label(model_id: str, entity_label: int) -> dict:
    """Look up an element by its integer IFC entity label (#NNN from the STEP file). Returns the same response as get_element_by_id. Use to cross-reference import log output like '[OK] #16535 LightGraphix...' directly against MCP queries."""
    return tool_get_element_by_label(model_id, entity_label)


@mcp.tool()
def get_representation(model_id: str, global_id: str) -> dict:
    """Get the representation structure of an element without tessellating geometry. Returns representation type, identifier, and items with IfcMappedItem details (mapping_target_is_identity, mapping_target_matrix). Use to detect baked rotations before geometry extraction."""
    return tool_get_representation(model_id, global_id)


@mcp.tool()
def get_elements_batch(model_id: str, global_ids: list, include: list | None = None) -> dict:
    """Batch query for multiple elements by GlobalId. include options: 'entity_label', 'placement', 'property_sets', 'local_bbox'. Default: ['entity_label', 'placement']. Avoids individual round-trips for files with 200+ fixtures."""
    return tool_get_elements_batch(model_id, global_ids, include)


@mcp.resource("ifc://model/{model_id}/summary")
def model_summary_resource(model_id: str) -> str:
    """Pre-computed text summary of the IFC model, suitable for AI context injection."""
    return get_summary(model_id)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
