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
        chain = []
        visited = set()
        current = element

        while True:
            if current.GlobalId in visited:
                break
            visited.add(current.GlobalId)

            # Try spatial containment first (IfcRelContainedInSpatialStructure)
            container = ifcopenshell.util.element.get_container(current)
            if container:
                chain.append({
                    "global_id": container.GlobalId,
                    "name": container.Name,
                    "type": container.is_a(),
                })
                current = container
                continue

            # Try aggregate parent (IfcRelAggregates) for spatial elements
            decomposes = getattr(current, "Decomposes", None)
            if decomposes:
                parent = decomposes[0].RelatingObject
                if parent.GlobalId not in visited:
                    chain.append({
                        "global_id": parent.GlobalId,
                        "name": parent.Name,
                        "type": parent.is_a(),
                    })
                    current = parent
                    continue
            break

        return {"global_id": global_id, "containment_chain": chain}
    except Exception as e:
        return {"error": "query_failed", "details": str(e)}


def _build_tree(element, visited=None) -> dict:
    if visited is None:
        visited = set()
    if element.GlobalId in visited:
        return {
            "global_id": element.GlobalId,
            "name": element.Name,
            "type": element.is_a(),
            "children": [],
            "note": "cycle detected",
        }
    visited.add(element.GlobalId)
    children = []
    # Decomposition (site > building > storey)
    for rel in element.IsDecomposedBy or []:
        for child in rel.RelatedObjects or []:
            children.append(_build_tree(child, visited))
    # Spaces contained at this level (storey > space)
    for rel in getattr(element, "ContainsElements", []) or []:
        for child in rel.RelatedElements or []:
            if child.is_a("IfcSpace"):
                children.append(_build_tree(child, visited))
    return {
        "global_id": element.GlobalId,
        "name": element.Name,
        "type": element.is_a(),
        "children": children,
    }
