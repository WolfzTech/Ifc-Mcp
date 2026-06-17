from ifc_manager import load_model, get_model, unload_model, list_models
from resources.model_summary import compute_and_store_summary, remove_summary


def tool_load_ifc_file(path: str) -> dict:
    try:
        model_id = load_model(path)
        model = get_model(model_id)
        projects = model.by_type("IfcProject")
        project_name = projects[0].Name if projects else "Unknown"
        element_count = len(model.by_type("IfcElement"))
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
        return {"error": "load_failed", "details": str(e)}


def tool_list_loaded_models() -> list[dict]:
    return list_models()


def tool_unload_ifc_file(model_id: str) -> dict:
    remove_summary(model_id)
    return {"success": unload_model(model_id)}
