import ifcopenshell.util.element
from ifc_manager import get_model


def tool_get_property_sets(model_id: str, global_id: str) -> dict:
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
        return ifcopenshell.util.element.get_psets(element, psets_only=True)
    except Exception as e:
        return {"error": "query_failed", "details": str(e)}


def tool_get_quantities(model_id: str, global_id: str) -> dict:
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
        return ifcopenshell.util.element.get_psets(element, qtos_only=True)
    except Exception as e:
        return {"error": "query_failed", "details": str(e)}


def tool_get_material(model_id: str, global_id: str) -> dict:
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
        material = ifcopenshell.util.element.get_material(element)
        if material is None:
            return {"name": None, "layers": None, "category": None}
        if material.is_a("IfcMaterial"):
            return {
                "name": material.Name,
                "layers": None,
                "category": getattr(material, "Category", None),
            }
        if material.is_a("IfcMaterialLayerSetUsage") or material.is_a("IfcMaterialLayerSet"):
            layer_set = material.ForLayerSet if material.is_a("IfcMaterialLayerSetUsage") else material
            layers = [
                {
                    "name": layer.Material.Name if layer.Material else None,
                    "thickness": layer.LayerThickness,
                }
                for layer in (layer_set.MaterialLayers or [])
            ]
            return {"name": getattr(layer_set, "LayerSetName", None), "layers": layers, "category": None}
        return {"name": str(material), "layers": None, "category": None}
    except Exception as e:
        return {"error": "query_failed", "details": str(e)}
