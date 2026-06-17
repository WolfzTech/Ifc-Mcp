import pytest
from pathlib import Path

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "sample.ifc"


@pytest.fixture(scope="session")
def sample_ifc_path() -> str:
    assert FIXTURE_PATH.exists(), (
        f"Fixture missing at {FIXTURE_PATH}. Run: uv run python tests/create_fixture.py"
    )
    return str(FIXTURE_PATH)
