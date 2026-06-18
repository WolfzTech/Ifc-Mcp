import ifcopenshell.util.element as util_el
from ifc_manager import get_model
from tools.property_tools import tool_get_property_sets
from tools.geometry_tools import tool_get_element_placement, tool_get_element_local_bbox


def tool_get_elements_by_type(
    model_id: str, ifc_type: str, limit: int = 100, offset: int = 0
) -> dict:
    try:
        model = get_model(model_id)
        all_elements = model.by_type(ifc_type)
        total = len(all_elements)
        page = all_elements[offset: offset + limit]
        return {
            "ifc_type": ifc_type,
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": [_to_dict(e) for e in page],
        }
    except KeyError as e:
        return {"error": "model_not_loaded", "details": str(e)}
    except Exception as e:
        return {"error": "query_failed", "details": str(e)}


def tool_get_element_by_id(model_id: str, global_id: str) -> dict:
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
        type_rels = getattr(element, "IsTypedBy", [])
        type_global_id = type_rels[0].RelatingType.GlobalId if type_rels else None

        rep_types = []
        if getattr(element, "Representation", None):
            for rep in element.Representation.Representations:
                for item in rep.Items:
                    t = item.is_a()
                    if t not in rep_types:
                        rep_types.append(t)

        return {
            "global_id": element.GlobalId,
            "entity_label": element.id(),
            "name": element.Name,
            "type": element.is_a(),
            "description": element.Description,
            "type_global_id": type_global_id,
            "representation_types": rep_types,
        }
    except Exception as e:
        return {"error": "query_failed", "details": str(e)}


def tool_search_elements(
    model_id: str,
    ifc_type: str | None = None,
    name_contains: str | None = None,
    pset_name: str | None = None,
    property_name: str | None = None,
    property_value: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict:
    if property_value is not None and property_name is None:
        return {"error": "invalid_filter", "details": "property_value requires property_name to be set"}
    try:
        model = get_model(model_id)
        base_type = ifc_type if ifc_type else "IfcElement"
        candidates = list(model.by_type(base_type))

        if name_contains:
            candidates = [
                e for e in candidates
                if getattr(e, "Name", None) and name_contains in e.Name
            ]

        if pset_name or property_name:
            filtered = []
            for e in candidates:
                psets = util_el.get_psets(e)
                if pset_name and pset_name not in psets:
                    continue
                if property_name:
                    target = {pset_name: psets[pset_name]} if pset_name else psets
                    found = any(
                        property_name in props
                        and (property_value is None or str(props[property_name]).lower() == str(property_value).lower())
                        for props in target.values()
                    )
                    if not found:
                        continue
                filtered.append(e)
            candidates = filtered

        total = len(candidates)
        page = candidates[offset: offset + limit]
        return {
            "ifc_type": base_type,
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": [_to_dict(e) for e in page],
        }
    except KeyError as e:
        return {"error": "model_not_loaded", "details": str(e)}
    except Exception as e:
        return {"error": "query_failed", "details": str(e)}


def tool_get_element_by_label(model_id: str, entity_label: int) -> dict:
    try:
        model = get_model(model_id)
    except KeyError as e:
        return {"error": "model_not_loaded", "details": str(e)}
    try:
        element = model.by_id(entity_label)
    except Exception:
        element = None
    if not element:
        return {"error": "element_not_found", "details": f"No element with entity label #{entity_label}"}
    type_rels = getattr(element, "IsTypedBy", [])
    type_global_id = type_rels[0].RelatingType.GlobalId if type_rels else None
    rep_types = []
    if getattr(element, "Representation", None):
        for rep in element.Representation.Representations:
            for item in rep.Items:
                t = item.is_a()
                if t not in rep_types:
                    rep_types.append(t)
    return {
        "global_id": element.GlobalId,
        "entity_label": element.id(),
        "name": getattr(element, "Name", None),
        "type": element.is_a(),
        "description": getattr(element, "Description", None),
        "type_global_id": type_global_id,
        "representation_types": rep_types,
    }


def tool_get_elements_batch(
    model_id: str,
    global_ids: list,
    include: list | None = None,
) -> dict:
    """
    Batch query for multiple elements by GlobalId.
    include options: "entity_label", "placement", "property_sets", "local_bbox"
    Default include: ["entity_label", "placement"]
    """
    if include is None:
        include = ["entity_label", "placement"]
    try:
        model = get_model(model_id)
    except KeyError as e:
        return {"error": "model_not_loaded", "details": str(e)}

    results = []
    for gid in global_ids:
        try:
            element = model.by_guid(gid)
        except RuntimeError:
            element = None
        if not element:
            results.append({"global_id": gid, "error": "element_not_found"})
            continue

        item = {
            "global_id": element.GlobalId,
            "name": getattr(element, "Name", None),
            "type": element.is_a(),
        }
        if "entity_label" in include:
            item["entity_label"] = element.id()
        if "placement" in include:
            item["placement"] = tool_get_element_placement(model_id, gid)
        if "property_sets" in include:
            item["property_sets"] = tool_get_property_sets(model_id, gid)
        if "local_bbox" in include:
            item["local_bbox"] = tool_get_element_local_bbox(model_id, gid)
        results.append(item)

    return {"model_id": model_id, "count": len(results), "items": results}


def _to_dict(element) -> dict:
    return {
        "global_id": getattr(element, "GlobalId", None),
        "name": getattr(element, "Name", None),
        "type": element.is_a(),
        "description": getattr(element, "Description", None),
        "entity_label": element.id(),
    }
