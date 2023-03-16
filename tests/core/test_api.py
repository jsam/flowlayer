import inspect
from typing import Any

import pytest

from datagears.core.api import EngineAPI, FeatureStoreAPI, NetworkAPI, NetworkPlotAPI


@pytest.mark.parametrize(
    "cls",
    [
        NetworkPlotAPI,
        NetworkAPI,
        EngineAPI,
        FeatureStoreAPI,
    ],
)
def test_api_definition_setup(cls: Any) -> None:
    """Test definition of all stubs."""
    methods = [m for m in dir(cls) if not m.startswith("_")]

    for method in methods:
        with pytest.raises(NotImplementedError):
            result = getattr(cls, method)
            if isinstance(result, property):
                result.fget(None)  # type: ignore
            else:
                params = [None] * len([p for p in inspect.signature(result).parameters.values() if p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD])

                result(*params)
