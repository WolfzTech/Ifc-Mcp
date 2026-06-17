import ifc_manager
from tools.file_tools import tool_load_ifc_file, tool_list_loaded_models, tool_unload_ifc_file


def setup_function():
    ifc_manager._registry.clear()
    ifc_manager._metadata.clear()


def test_load_returns_model_info(sample_ifc_path):
    result = tool_load_ifc_file(sample_ifc_path)
    assert "error" not in result
    assert "model_id" in result
    assert result["project_name"] == "Test Project"
    assert result["schema"] == "IFC4"
    assert result["element_count"] >= 3


def test_load_missing_file_returns_error():
    result = tool_load_ifc_file("/nonexistent/file.ifc")
    assert result["error"] == "file_not_found"
    assert "details" in result


def test_list_models_after_load(sample_ifc_path):
    tool_load_ifc_file(sample_ifc_path)
    result = tool_list_loaded_models()
    assert len(result) == 1
    assert "model_id" in result[0]


def test_unload_model(sample_ifc_path):
    model_id = tool_load_ifc_file(sample_ifc_path)["model_id"]
    result = tool_unload_ifc_file(model_id)
    assert result["success"] is True
    assert len(tool_list_loaded_models()) == 0


def test_unload_unknown_model():
    result = tool_unload_ifc_file("unknown_id")
    assert result["success"] is False
