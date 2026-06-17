import ifcopenshell.util.element as util_el
from ifc_manager import get_model


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
        return _to_dict(element)
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
                        and (property_value is None or str(props[property_name]) == property_value)
                        for props in target.values()
                    )
                    if not found:
                        continue
                filtered.append(e)
            candidates = filtered

        total = len(candidates)
        page = candidates[offset: offset + limit]
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": [_to_dict(e) for e in page],
        }
    except KeyError as e:
        return {"error": "model_not_loaded", "details": str(e)}
    except Exception as e:
        return {"error": "query_failed", "details": str(e)}


def _to_dict(element) -> dict:
    return {
        "global_id": getattr(element, "GlobalId", None),
        "name": getattr(element, "Name", None),
        "type": element.is_a(),
        "description": getattr(element, "Description", None),
    }
