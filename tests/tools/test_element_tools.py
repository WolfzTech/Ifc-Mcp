import ifc_manager
from tools.file_tools import tool_load_ifc_file
from tools.element_tools import (
    tool_get_elements_by_type,
    tool_get_element_by_id,
    tool_search_elements,
    tool_get_element_by_label,
    tool_get_elements_batch,
)
from resources.model_summary import _summaries


def setup_function():
    ifc_manager._registry.clear()
    ifc_manager._metadata.clear()
    _summaries.clear()


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


def test_search_by_property_value(sample_ifc_path):
    model_id = tool_load_ifc_file(sample_ifc_path)["model_id"]
    result = tool_search_elements(
        model_id,
        pset_name="Pset_WallCommon",
        property_name="FireRating",
        property_value="REI60",
    )
    assert result["total"] == 1
    assert result["items"][0]["name"] == "Wall 001"


def test_get_element_by_id_includes_entity_label_and_type(sample_model_id):
    walls = tool_get_elements_by_type(sample_model_id, "IfcWall", limit=1)
    gid = walls["items"][0]["global_id"]
    result = tool_get_element_by_id(sample_model_id, gid)
    assert "error" not in result
    assert isinstance(result["entity_label"], int)
    assert result["entity_label"] > 0
    assert "type_global_id" in result  # may be None if no type assigned
    assert isinstance(result["representation_types"], list)


def test_get_element_by_label(sample_model_id):
    walls = tool_get_elements_by_type(sample_model_id, "IfcWall", limit=1)
    entity_label = walls["items"][0]["entity_label"]
    result = tool_get_element_by_label(sample_model_id, entity_label)
    assert "error" not in result
    assert result["entity_label"] == entity_label
    assert result["type"] == "IfcWall"


def test_get_element_by_label_invalid(sample_model_id):
    result = tool_get_element_by_label(sample_model_id, 999999)
    assert result["error"] == "element_not_found"


def test_get_elements_batch(sample_model_id):
    walls = tool_get_elements_by_type(sample_model_id, "IfcWall")
    global_ids = [w["global_id"] for w in walls["items"][:2]]
    result = tool_get_elements_batch(sample_model_id, global_ids, include=["entity_label"])
    assert "error" not in result
    assert result["count"] == 2
    for item in result["items"]:
        assert "entity_label" in item


def test_get_elements_batch_invalid_id(sample_model_id):
    result = tool_get_elements_batch(sample_model_id, ["INVALID_GUID"])
    assert result["items"][0]["error"] == "element_not_found"
