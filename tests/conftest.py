import pytest
from pathlib import Path

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "sample.ifc"


@pytest.fixture(scope="session")
def sample_ifc_path() -> str:
    assert FIXTURE_PATH.exists(), (
        f"Fixture missing at {FIXTURE_PATH}. Run: uv run python tests/create_fixture.py"
    )
    return str(FIXTURE_PATH)


@pytest.fixture()
def sample_model_id(sample_ifc_path):
    import ifc_manager
    from tools.file_tools import tool_load_ifc_file
    from resources.model_summary import _summaries
    ifc_manager._registry.clear()
    ifc_manager._metadata.clear()
    _summaries.clear()
    return tool_load_ifc_file(sample_ifc_path)["model_id"]
