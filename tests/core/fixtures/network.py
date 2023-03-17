import pytest

from flowlayer.core.network import Network


@pytest.fixture
def mynetwork() -> Network:
    """Testing fixture for a feature."""
    from flowlayer.core.network import Network
    from tests.fixtures import my_out

    network = Network("my-network", outputs=[my_out])
    return network
