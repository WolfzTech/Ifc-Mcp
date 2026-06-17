from collections import Counter
import ifcopenshell
from ifc_manager import get_model

_summaries: dict[str, str] = {}


def compute_and_store_summary(model_id: str) -> None:
    model = get_model(model_id)
    _summaries[model_id] = _build_summary(model, model_id)


def get_summary(model_id: str) -> str:
    return _summaries.get(model_id, f"Model '{model_id}' not loaded.")


def remove_summary(model_id: str) -> None:
    _summaries.pop(model_id, None)


def _build_summary(model: ifcopenshell.file, model_id: str) -> str:
    projects = model.by_type("IfcProject")
    project_name = projects[0].Name if projects else "Unknown"
    elements = model.by_type("IfcElement")
    counts = Counter(e.is_a() for e in elements)
    top_types = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:10]
    storeys = model.by_type("IfcBuildingStorey")

    lines = [
        "# IFC Model Summary",
        f"Model ID: {model_id}",
        f"Project: {project_name}",
        f"Schema: {model.schema}",
        f"Total elements: {len(elements)}",
        "",
        "## Element counts by type:",
    ]
    for ifc_type, count in top_types:
        lines.append(f"  {ifc_type}: {count}")
    lines += ["", f"## Storeys ({len(storeys)}):"]
    for s in storeys:
        lines.append(f"  - {getattr(s, 'Name', 'Unnamed')}")
    return "\n".join(lines)
