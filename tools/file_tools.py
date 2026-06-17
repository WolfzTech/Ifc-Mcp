from ifc_manager import load_model, get_model, unload_model, list_models
from resources.model_summary import compute_and_store_summary, remove_summary, has_summary


def tool_load_ifc_file(path: str) -> dict:
    model_id = None
    try:
        model_id = load_model(path)
        model = get_model(model_id)
        projects = model.by_type("IfcProject")
        project_name = projects[0].Name if projects else "Unknown"
        element_count = len(model.by_type("IfcElement"))
        if not has_summary(model_id):
            compute_and_store_summary(model_id)
        return {
            "model_id": model_id,
            "project_name": project_name,
            "schema": model.schema,
            "element_count": element_count,
        }
    except FileNotFoundError as e:
        return {"error": "file_not_found", "details": str(e)}
    except Exception as e:
        if model_id is not None:
            unload_model(model_id)
            remove_summary(model_id)
        return {"error": "load_failed", "details": str(e)}


def tool_list_loaded_models() -> list[dict]:
    return list_models()


def tool_unload_ifc_file(model_id: str) -> dict:
    if not unload_model(model_id):
        return {"error": "model_not_loaded", "details": f"Model '{model_id}' not found"}
    remove_summary(model_id)
    return {"success": True}
