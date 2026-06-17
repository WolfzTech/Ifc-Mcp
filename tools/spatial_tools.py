import ifcopenshell.util.element
from ifc_manager import get_model


def tool_get_spatial_structure(model_id: str) -> dict:
    try:
        model = get_model(model_id)
        projects = model.by_type("IfcProject")
        if not projects:
            return {"error": "no_project", "details": "No IfcProject found in model"}
        return _build_tree(projects[0])
    except KeyError as e:
        return {"error": "model_not_loaded", "details": str(e)}
    except Exception as e:
        return {"error": "query_failed", "details": str(e)}


def tool_get_element_containment(model_id: str, global_id: str) -> dict:
    try:
        model = get_model(model_id)
    except KeyError as e:
        return {"error": "model_not_loaded", "details": str(e)}
    try:
        element = model.by_guid(global_id)
    except RuntimeError:
        return {"error": "element_not_found", "details": f"No element with GlobalId '{global_id}'"}
    if not element:
        return {"error": "element_not_found", "details": f"No element with GlobalId '{global_id}'"}
    try:
        result = {}
        container = ifcopenshell.util.element.get_container(element)
        while container:
            result[container.is_a()] = {
                "name": getattr(container, "Name", None),
                "global_id": container.GlobalId,
            }
            container = ifcopenshell.util.element.get_container(container)
        return result
    except Exception as e:
        return {"error": "query_failed", "details": str(e)}


def _build_tree(element) -> dict:
    node = {
        "type": element.is_a(),
        "name": getattr(element, "Name", None),
        "global_id": getattr(element, "GlobalId", None),
        "children": [],
    }
    for rel in getattr(element, "IsDecomposedBy", []) or []:
        for child in rel.RelatedObjects:
            node["children"].append(_build_tree(child))
    return node
