import ifc_manager
from tools.file_tools import tool_load_ifc_file
from tools.element_tools import tool_get_elements_by_type, tool_get_element_by_id, tool_search_elements


def setup_function():
    ifc_manager._registry.clear()
    ifc_manager._metadata.clear()


def test_get_elements_by_type_walls(sample_ifc_path):
    model_id = tool_load_ifc_file(sample_ifc_path)["model_id"]
    result = tool_get_elements_by_type(model_id, "IfcWall")
    assert "error" not in result
    assert result["total"] == 2
    assert len(result["items"]) == 2
    assert all(item["type"] == "IfcWall" for item in result["items"])


def test_get_elements_by_type_pagination(sample_ifc_path):
    model_id = tool_load_ifc_file(sample_ifc_path)["model_id"]
    page1 = tool_get_elements_by_type(model_id, "IfcWall", limit=1, offset=0)
    page2 = tool_get_elements_by_type(model_id, "IfcWall", limit=1, offset=1)
    assert len(page1["items"]) == 1
    assert len(page2["items"]) == 1
    assert page1["items"][0]["global_id"] != page2["items"][0]["global_id"]


def test_get_elements_by_type_empty(sample_ifc_path):
    model_id = tool_load_ifc_file(sample_ifc_path)["model_id"]
    result = tool_get_elements_by_type(model_id, "IfcBeam")
    assert result["total"] == 0
    assert result["items"] == []


def test_get_element_by_id(sample_ifc_path):
    model_id = tool_load_ifc_file(sample_ifc_path)["model_id"]
    walls = tool_get_elements_by_type(model_id, "IfcWall")
    global_id = walls["items"][0]["global_id"]
    result = tool_get_element_by_id(model_id, global_id)
    assert "error" not in result
    assert result["global_id"] == global_id
    assert result["type"] == "IfcWall"


def test_get_element_by_id_not_found(sample_ifc_path):
    model_id = tool_load_ifc_file(sample_ifc_path)["model_id"]
    result = tool_get_element_by_id(model_id, "NONEXISTENT00000")
    assert result["error"] == "element_not_found"


def test_search_by_type(sample_ifc_path):
    model_id = tool_load_ifc_file(sample_ifc_path)["model_id"]
    result = tool_search_elements(model_id, ifc_type="IfcDoor")
    assert result["total"] == 1
    assert result["items"][0]["type"] == "IfcDoor"


def test_search_by_name_contains(sample_ifc_path):
    model_id = tool_load_ifc_file(sample_ifc_path)["model_id"]
    result = tool_search_elements(model_id, name_contains="Wall 001")
    assert result["total"] == 1
    assert result["items"][0]["name"] == "Wall 001"
