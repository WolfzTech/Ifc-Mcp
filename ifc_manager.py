import hashlib
from pathlib import Path
import ifcopenshell

_registry: dict[str, ifcopenshell.file] = {}
_metadata: dict[str, dict] = {}


def load_model(path: str) -> str:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Path '{path}' does not exist")
    if p.suffix.lower() != ".ifc":
        raise ValueError(f"Expected an .ifc file, got '{p.suffix}'")
    model_id = _make_model_id(p)
    if model_id not in _registry:
        _registry[model_id] = ifcopenshell.open(str(p))
        _metadata[model_id] = {"path": str(p), "model_id": model_id}
    return model_id


def get_model(model_id: str) -> ifcopenshell.file:
    if model_id not in _registry:
        raise KeyError(f"Model '{model_id}' not loaded. Call load_ifc_file first.")
    return _registry[model_id]


def unload_model(model_id: str) -> bool:
    if model_id in _registry:
        del _registry[model_id]
        del _metadata[model_id]
        return True
    return False


def list_models() -> list[dict]:
    return [{"model_id": mid, **meta} for mid, meta in _metadata.items()]


def _make_model_id(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return f"{path.stem}_{h.hexdigest()[:12]}"
