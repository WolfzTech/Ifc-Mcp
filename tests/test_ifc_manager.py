import pytest
import ifc_manager


def setup_function():
    ifc_manager._registry.clear()
    ifc_manager._metadata.clear()


def test_load_returns_model_id(sample_ifc_path):
    model_id = ifc_manager.load_model(sample_ifc_path)
    assert isinstance(model_id, str)
    assert len(model_id) > 0


def test_load_bad_path_raises():
    with pytest.raises(FileNotFoundError):
        ifc_manager.load_model("/nonexistent/path.ifc")


def test_get_returns_model(sample_ifc_path):
    model_id = ifc_manager.load_model(sample_ifc_path)
    model = ifc_manager.get_model(model_id)
    assert model is not None


def test_get_unknown_raises():
    with pytest.raises(KeyError):
        ifc_manager.get_model("nonexistent_id")


def test_unload_removes_from_registry(sample_ifc_path):
    model_id = ifc_manager.load_model(sample_ifc_path)
    result = ifc_manager.unload_model(model_id)
    assert result is True
    assert model_id not in ifc_manager._registry


def test_unload_unknown_returns_false():
    assert ifc_manager.unload_model("nonexistent") is False


def test_list_models(sample_ifc_path):
    ifc_manager.load_model(sample_ifc_path)
    models = ifc_manager.list_models()
    assert len(models) == 1
    assert "model_id" in models[0]
    assert "path" in models[0]
