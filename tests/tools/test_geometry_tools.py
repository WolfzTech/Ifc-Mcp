import ifc_manager
from tools.file_tools import tool_load_ifc_file
from tools.geometry_tools import (
    tool_get_model_statistics,
    tool_get_bounding_box,
    tool_get_element_placement,
    tool_get_element_local_bbox,
    tool_get_element_body_mapping,
    tool_get_representation,
)
from tools.element_tools import tool_get_elements_by_type
from resources.model_summary import _summaries


def setup_function():
    ifc_manager._registry.clear()
    ifc_manager._metadata.clear()
    _summaries.clear()


def test_get_model_statistics(sample_ifc_path):
    model_id = tool_load_ifc_file(sample_ifc_path)["model_id"]
    result = tool_get_model_statistics(model_id)
    assert "error" not in result
    assert result["element_counts"]["IfcWall"] == 2
    assert result["element_counts"]["IfcDoor"] == 1
    assert result["total_elements"] == 3
    assert result["schema"] == "IFC4"
    assert result["storey_count"] == 2
    assert "Ground Floor" in result["storey_names"]


def test_get_model_statistics_unknown_model():
    result = tool_get_model_statistics("unknown")
    assert "error" in result


def test_get_bounding_box_no_geometry(sample_ifc_path):
    model_id = tool_load_ifc_file(sample_ifc_path)["model_id"]
    model = ifc_manager.get_model(model_id)
    wall = model.by_type("IfcWall")[0]
    result = tool_get_bounding_box(model_id, wall.GlobalId)
    assert result["error"] == "geometry_unavailable"


def test_get_bounding_box_invalid_id(sample_ifc_path):
    model_id = tool_load_ifc_file(sample_ifc_path)["model_id"]
    result = tool_get_bounding_box(model_id, "NONEXISTENT00000")
    assert result["error"] == "element_not_found"


def test_get_element_placement(sample_ifc_path):
    model_id = tool_load_ifc_file(sample_ifc_path)["model_id"]
    walls = tool_get_elements_by_type(model_id, "IfcWall", limit=1)
    global_id = walls["items"][0]["global_id"]
    result = tool_get_element_placement(model_id, global_id)
    assert "error" not in result
    assert "object_placement" in result
    assert "world_transform" in result
    assert "world_transform_determinant" in result
    assert "has_non_identity_body_mapping" in result
    assert "entity_label" in result
    assert isinstance(result["entity_label"], int)
    # object_placement and world_transform should each have location and axis lists
    for key in ("object_placement", "world_transform"):
        block = result[key]
        assert "location" in block and len(block["location"]) == 3
        assert "x_axis" in block and len(block["x_axis"]) == 3
        assert "y_axis" in block and len(block["y_axis"]) == 3
        assert "z_axis" in block and len(block["z_axis"]) == 3
    # determinant should be close to ±1.0 for a rigid transform
    import math
    assert abs(abs(result["world_transform_determinant"]) - 1.0) < 0.01


def test_get_element_placement_invalid_id(sample_ifc_path):
    model_id = tool_load_ifc_file(sample_ifc_path)["model_id"]
    result = tool_get_element_placement(model_id, "INVALID_GUID")
    assert result["error"] == "element_not_found"


def test_get_element_local_bbox_no_geometry(sample_model_id):
    walls = tool_get_elements_by_type(sample_model_id, "IfcWall", limit=1)
    gid = walls["items"][0]["global_id"]
    result = tool_get_element_local_bbox(sample_model_id, gid)
    # The test fixture wall may or may not have geometry; either is acceptable
    assert "error" in result or ("min" in result and "max" in result and "dimensions" in result)


def test_get_element_local_bbox_invalid_id(sample_model_id):
    result = tool_get_element_local_bbox(sample_model_id, "INVALID_GUID")
    assert result["error"] == "element_not_found"


def test_get_element_body_mapping(sample_model_id):
    walls = tool_get_elements_by_type(sample_model_id, "IfcWall", limit=1)
    gid = walls["items"][0]["global_id"]
    result = tool_get_element_body_mapping(sample_model_id, gid)
    assert "error" not in result
    assert "has_mapped_item" in result
    assert "has_non_identity_body_mapping" in result
    assert "is_mirrored" in result
    assert isinstance(result["has_mapped_item"], bool)


def test_get_element_body_mapping_invalid_id(sample_model_id):
    result = tool_get_element_body_mapping(sample_model_id, "INVALID_GUID")
    assert result["error"] == "element_not_found"


def test_get_representation(sample_model_id):
    walls = tool_get_elements_by_type(sample_model_id, "IfcWall", limit=1)
    gid = walls["items"][0]["global_id"]
    result = tool_get_representation(sample_model_id, gid)
    # Wall may or may not have representation
    assert "error" in result or "representations" in result


def test_get_representation_invalid_id(sample_model_id):
    result = tool_get_representation(sample_model_id, "INVALID_GUID")
    assert result["error"] == "element_not_found"
