import pytest

from datagears.core.api import FeatureStoreAPI


@pytest.fixture
def feature_store() -> FeatureStoreAPI:
    """Default feature store fixture."""
    from datagears.core.stores import FeatureStore

    return FeatureStore()
