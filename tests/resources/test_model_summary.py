import ifc_manager
from tools.file_tools import tool_load_ifc_file, tool_unload_ifc_file
from resources.model_summary import compute_and_store_summary, get_summary, remove_summary


def setup_function():
    ifc_manager._registry.clear()
    ifc_manager._metadata.clear()


def test_compute_and_get_summary(sample_ifc_path):
    model_id = tool_load_ifc_file(sample_ifc_path)["model_id"]
    compute_and_store_summary(model_id)
    summary = get_summary(model_id)
    assert "Test Project" in summary
    assert "IFC4" in summary
    assert "IfcWall" in summary
    assert "Ground Floor" in summary


def test_get_summary_unknown_model():
    result = get_summary("nonexistent_id")
    assert "not loaded" in result


def test_remove_summary(sample_ifc_path):
    model_id = tool_load_ifc_file(sample_ifc_path)["model_id"]
    compute_and_store_summary(model_id)
    remove_summary(model_id)
    result = get_summary(model_id)
    assert "not loaded" in result
