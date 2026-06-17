import ifc_manager
from tools.file_tools import tool_load_ifc_file
from tools.spatial_tools import tool_get_spatial_structure, tool_get_element_containment
from resources.model_summary import _summaries


def setup_function():
    ifc_manager._registry.clear()
    ifc_manager._metadata.clear()
    _summaries.clear()


def test_get_spatial_structure(sample_ifc_path):
    model_id = tool_load_ifc_file(sample_ifc_path)["model_id"]
    tree = tool_get_spatial_structure(model_id)
    assert "error" not in tree
    assert tree["type"] == "IfcProject"
    assert tree["name"] == "Test Project"
    site = tree["children"][0]
    assert site["type"] == "IfcSite"
    building = site["children"][0]
    assert building["type"] == "IfcBuilding"
    storey_names = [s["name"] for s in building["children"]]
    assert "Ground Floor" in storey_names
    assert "First Floor" in storey_names


def test_get_spatial_structure_unknown_model():
    result = tool_get_spatial_structure("unknown_id")
    assert "error" in result


def test_get_element_containment(sample_ifc_path):
    model_id = tool_load_ifc_file(sample_ifc_path)["model_id"]
    model = ifc_manager.get_model(model_id)
    wall = model.by_type("IfcWall")[0]
    result = tool_get_element_containment(model_id, wall.GlobalId)
    assert "error" not in result
    assert "containment_chain" in result
    chain = result["containment_chain"]
    storey = next((c for c in chain if c["type"] == "IfcBuildingStorey"), None)
    assert storey is not None
    assert storey["name"] == "Ground Floor"


def test_get_element_containment_invalid_guid(sample_ifc_path):
    model_id = tool_load_ifc_file(sample_ifc_path)["model_id"]
    result = tool_get_element_containment(model_id, "INVALID_GUID_000")
    assert result["error"] == "element_not_found"
