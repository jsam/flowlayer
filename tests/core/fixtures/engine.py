import os
from pathlib import Path
from typing import Iterator

import pytest
from filelock import FileLock

from datagears.core.api import EngineAPI


@pytest.fixture(scope="session")
def dask_engine(egg_path: Path) -> Iterator[EngineAPI]:
    """Create and setup dask engine."""
    from datagears.core.engine import DaskEngine

    scheduler: str = os.getenv("DASK_SCHEDULER_URI", "0.0.0.0:8786")
    engine = DaskEngine(
        f"{scheduler}",
        ["networkx", "numpy"],
        egg_path,
    )
    assert engine.is_ready() is False

    with FileLock("dask_engine.lock"):
        engine.setup()

        yield engine

        _executor = engine._executor  # type: ignore
        engine._executor = None  # type: ignore
        with pytest.raises(ValueError):
            engine.teardown()

        engine._executor = _executor  # type: ignore
        engine.teardown()
