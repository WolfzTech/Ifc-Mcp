import ifc_manager
from tools.file_tools import tool_load_ifc_file
from tools.geometry_tools import tool_get_model_statistics, tool_get_bounding_box
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
