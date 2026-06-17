from collections import Counter
import ifcopenshell.geom
import ifcopenshell.util.placement
from ifc_manager import get_model


def tool_get_model_statistics(model_id: str) -> dict:
    try:
        model = get_model(model_id)
    except KeyError as e:
        return {"error": "model_not_loaded", "details": str(e)}
    counts = Counter(e.is_a() for e in model.by_type("IfcElement"))
    projects = model.by_type("IfcProject")
    project_name = projects[0].Name if projects else "Unknown"
    storeys = model.by_type("IfcBuildingStorey")
    storey_names = [s.Name for s in storeys]
    return {
        "model_id": model_id,
        "project_name": project_name,
        "schema": model.schema,
        "total_elements": sum(counts.values()),
        "element_counts": dict(counts.most_common(20)),
        "storey_count": len(storeys),
        "storey_names": storey_names,
    }


def tool_get_bounding_box(model_id: str, global_id: str) -> dict:
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
    settings = ifcopenshell.geom.settings()
    settings.set("use-world-coords", True)
    try:
        shape = ifcopenshell.geom.create_shape(settings, element)
    except Exception:
        return {"error": "geometry_unavailable", "details": "Element has no geometry representation"}
    verts = shape.geometry.verts
    if not verts:
        return {"error": "geometry_unavailable", "details": "Element geometry has no vertices"}
    xs = verts[0::3]
    ys = verts[1::3]
    zs = verts[2::3]
    return {
        "global_id": global_id,
        "min": {"x": min(xs), "y": min(ys), "z": min(zs)},
        "max": {"x": max(xs), "y": max(ys), "z": max(zs)},
        "dimensions": {
            "width": max(xs) - min(xs),
            "depth": max(ys) - min(ys),
            "height": max(zs) - min(zs),
        },
    }


def tool_get_element_placement(model_id: str, global_id: str) -> dict:
    try:
        model = get_model(model_id)
    except KeyError as e:
        return {"error": "model_not_loaded", "details": str(e)}
    try:
        element = model.by_guid(global_id)
    except RuntimeError:
        element = None
    if not element:
        return {"error": "element_not_found", "details": f"No element with GlobalId '{global_id}'"}
    if not getattr(element, "ObjectPlacement", None):
        return {"error": "placement_unavailable", "details": "Element has no ObjectPlacement"}
    m = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)
    # m is a 4x4 numpy array; columns are X, Y, Z axes; last column is translation
    return {
        "global_id": global_id,
        "location": {"x": float(m[0, 3]), "y": float(m[1, 3]), "z": float(m[2, 3])},
        "x_axis": {"x": float(m[0, 0]), "y": float(m[1, 0]), "z": float(m[2, 0])},
        "y_axis": {"x": float(m[0, 1]), "y": float(m[1, 1]), "z": float(m[2, 1])},
        "z_axis": {"x": float(m[0, 2]), "y": float(m[1, 2]), "z": float(m[2, 2])},
    }
