import ifc_manager
from tools.file_tools import tool_load_ifc_file
from tools.property_tools import tool_get_property_sets, tool_get_quantities, tool_get_material, tool_get_property_sets_detail
from tools.element_tools import tool_get_elements_by_type
from resources.model_summary import _summaries


def setup_function():
    ifc_manager._registry.clear()
    ifc_manager._metadata.clear()
    _summaries.clear()


def test_get_property_sets(sample_ifc_path):
    model_id = tool_load_ifc_file(sample_ifc_path)["model_id"]
    model = ifc_manager.get_model(model_id)
    wall1 = next(w for w in model.by_type("IfcWall") if w.Name == "Wall 001")
    result = tool_get_property_sets(model_id, wall1.GlobalId)
    assert "error" not in result
    assert "entity_label" in result
    assert isinstance(result["entity_label"], int)
    assert "psets" in result
    assert "Pset_WallCommon" in result["psets"]
    assert result["psets"]["Pset_WallCommon"]["FireRating"] == "REI60"
    assert result["psets"]["Pset_WallCommon"]["IsExternal"] is True


def test_get_property_sets_no_psets(sample_ifc_path):
    model_id = tool_load_ifc_file(sample_ifc_path)["model_id"]
    model = ifc_manager.get_model(model_id)
    wall2 = next(w for w in model.by_type("IfcWall") if w.Name == "Wall 002")
    result = tool_get_property_sets(model_id, wall2.GlobalId)
    assert "error" not in result
    assert result["psets"] == {}


def test_get_quantities(sample_ifc_path):
    model_id = tool_load_ifc_file(sample_ifc_path)["model_id"]
    model = ifc_manager.get_model(model_id)
    wall1 = next(w for w in model.by_type("IfcWall") if w.Name == "Wall 001")
    result = tool_get_quantities(model_id, wall1.GlobalId)
    assert "error" not in result
    assert "Qto_WallBaseQuantities" in result
    assert result["Qto_WallBaseQuantities"]["Length"] == 5.0


def test_get_quantities_none(sample_ifc_path):
    model_id = tool_load_ifc_file(sample_ifc_path)["model_id"]
    model = ifc_manager.get_model(model_id)
    wall2 = next(w for w in model.by_type("IfcWall") if w.Name == "Wall 002")
    result = tool_get_quantities(model_id, wall2.GlobalId)
    assert "error" not in result
    assert result == {}


def test_get_material_not_assigned(sample_ifc_path):
    model_id = tool_load_ifc_file(sample_ifc_path)["model_id"]
    model = ifc_manager.get_model(model_id)
    door = model.by_type("IfcDoor")[0]
    result = tool_get_material(model_id, door.GlobalId)
    assert "error" not in result
    assert result["name"] is None


def test_get_property_sets_invalid_id(sample_ifc_path):
    model_id = tool_load_ifc_file(sample_ifc_path)["model_id"]
    result = tool_get_property_sets(model_id, "NONEXISTENT00000")
    assert result["error"] == "element_not_found"


def test_get_property_sets_detail(sample_model_id):
    walls = tool_get_elements_by_type(sample_model_id, "IfcWall", limit=1)
    gid = walls["items"][0]["global_id"]
    result = tool_get_property_sets_detail(sample_model_id, gid)
    assert "error" not in result
    assert "instance" in result
    assert "type" in result
    assert isinstance(result["instance"], dict)
    assert isinstance(result["type"], dict)


def test_get_property_sets_detail_invalid_id(sample_model_id):
    result = tool_get_property_sets_detail(sample_model_id, "INVALID_GUID")
    assert result["error"] == "element_not_found"
