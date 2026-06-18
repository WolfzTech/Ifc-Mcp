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
        "entity_label": element.id(),
        "min": {"x": min(xs), "y": min(ys), "z": min(zs)},
        "max": {"x": max(xs), "y": max(ys), "z": max(zs)},
        "dimensions": {
            "width": max(xs) - min(xs),
            "depth": max(ys) - min(ys),
            "height": max(zs) - min(zs),
        },
    }


def tool_get_element_local_bbox(model_id: str, global_id: str) -> dict:
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
    settings = ifcopenshell.geom.settings()
    # Do NOT set use-world-coords — local space is the default
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


def tool_get_representation(model_id: str, global_id: str) -> dict:
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
    if not getattr(element, "Representation", None):
        return {"error": "no_representation", "details": "Element has no geometry representation"}

    import numpy as np
    identity = np.eye(4)
    representations = []
    for rep in element.Representation.Representations:
        items = []
        for item in rep.Items:
            item_info = {"type": item.is_a()}
            if item.is_a("IfcMappedItem"):
                target = item.MappingTarget
                m = _cart_transform_to_matrix(target)
                is_identity = bool(np.allclose(m, identity, atol=1e-6))
                item_info["mapping_target_is_identity"] = is_identity
                item_info["mapping_target_matrix"] = _mat_to_axes_dict(m) if not is_identity else None
            items.append(item_info)
        representations.append({
            "type": rep.RepresentationType,
            "identifier": rep.RepresentationIdentifier,
            "items": items,
        })
    return {
        "global_id": global_id,
        "entity_label": element.id(),
        "representations": representations,
    }


def tool_get_element_body_mapping(model_id: str, global_id: str) -> dict:
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

    # --- ObjectPlacement (OPM) matrix ---
    opm = None
    if getattr(element, "ObjectPlacement", None):
        opm = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)

    # --- Body mapping matrix from IfcMappedItem ---
    body_matrix = None
    has_mapped_item = False
    if getattr(element, "Representation", None):
        for rep in element.Representation.Representations:
            for item in rep.Items:
                if item.is_a("IfcMappedItem"):
                    has_mapped_item = True
                    target = item.MappingTarget
                    body_matrix = _cart_transform_to_matrix(target)
                    break
            if has_mapped_item:
                break

    # --- World transform = OPM @ body_mapping (if both exist) ---
    if opm is not None and body_matrix is not None:
        world = opm @ body_matrix
    elif opm is not None:
        world = opm
    else:
        world = None

    # --- Determinant of upper-left 3x3 (rotation + scale) ---
    det = None
    is_mirrored = None
    if world is not None:
        import numpy.linalg as la
        det = float(la.det(world[:3, :3]))
        is_mirrored = det < 0

    def mat_to_list(m):
        return [list(map(float, row)) for row in m]

    # Identity check (within tolerance)
    import numpy
    identity = numpy.eye(4)
    has_non_identity = body_matrix is not None and not numpy.allclose(body_matrix, identity, atol=1e-6)

    return {
        "global_id": global_id,
        "has_mapped_item": has_mapped_item,
        "has_non_identity_body_mapping": has_non_identity,
        "body_mapping_matrix": mat_to_list(body_matrix) if body_matrix is not None else None,
        "world_transform": mat_to_list(world) if world is not None else None,
        "world_transform_determinant": det,
        "is_mirrored": is_mirrored,
    }


def _cart_transform_to_matrix(transform):
    import numpy as np
    scale = float(transform.Scale) if transform.Scale is not None else 1.0
    origin = list(transform.LocalOrigin.Coordinates)
    ax1 = list(transform.Axis1.DirectionRatios) if transform.Axis1 else [1.0, 0.0, 0.0]
    ax2 = list(transform.Axis2.DirectionRatios) if transform.Axis2 else [0.0, 1.0, 0.0]
    ax3 = list(transform.Axis3.DirectionRatios) if transform.Axis3 else [0.0, 0.0, 1.0]
    m = np.array([
        [ax1[0]*scale, ax2[0]*scale, ax3[0]*scale, origin[0]],
        [ax1[1]*scale, ax2[1]*scale, ax3[1]*scale, origin[1]],
        [ax1[2]*scale, ax2[2]*scale, ax3[2]*scale, origin[2]],
        [0.0,          0.0,          0.0,           1.0      ],
    ])
    return m


def _mat_to_axes_dict(m):
    return {
        "location": [float(m[0, 3]), float(m[1, 3]), float(m[2, 3])],
        "x_axis":   [float(m[0, 0]), float(m[1, 0]), float(m[2, 0])],
        "y_axis":   [float(m[0, 1]), float(m[1, 1]), float(m[2, 1])],
        "z_axis":   [float(m[0, 2]), float(m[1, 2]), float(m[2, 2])],
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

    import numpy as np
    import numpy.linalg as la

    opm = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)

    # Find body mapping matrix from IfcMappedItem
    body_matrix = None
    if getattr(element, "Representation", None):
        for rep in element.Representation.Representations:
            for item in rep.Items:
                if item.is_a("IfcMappedItem"):
                    body_matrix = _cart_transform_to_matrix(item.MappingTarget)
                    break
            if body_matrix is not None:
                break

    identity = np.eye(4)
    has_non_identity = body_matrix is not None and not np.allclose(body_matrix, identity, atol=1e-6)

    if body_matrix is not None:
        world = opm @ body_matrix
    else:
        world = opm

    det = float(la.det(world[:3, :3]))

    return {
        "global_id": global_id,
        "entity_label": element.id(),
        "object_placement": _mat_to_axes_dict(opm),
        "world_transform": _mat_to_axes_dict(world),
        "world_transform_determinant": det,
        "has_non_identity_body_mapping": has_non_identity,
    }
