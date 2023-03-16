import pytest

from datagears.core.network import Network


@pytest.fixture
def myfeature() -> Network:
    """Testing fixture for a feature."""
    from datagears.core.network import Network
    from datagears.features.dummy import my_out

    network = Network("my-network", outputs=[my_out])
    return network


@pytest.fixture
def store_feature() -> Network:
    """Testing fixture for a feature."""
    from datagears.core.network import Network
    from datagears.core.stores import FeatureStore
    from datagears.features.dummy import my_out

    network = Network("my-network", outputs=[my_out], feature_store=FeatureStore())
    return network
