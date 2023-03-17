import pytest
from numpy import array, ndarray

from flowlayer.core.network import Depends, Maybe, Network


def add(a: int, b: int = 10) -> int:
    return a + b


def reduce(c1: int, sum: Maybe[int] = Depends(add)) -> int:
    result = sum - c1
    return result


def add_one() -> int:
    return 1


def my_out(reduced: Maybe[int] = Depends(reduce), add_one: Maybe[int] = Depends(add_one)) -> ndarray:
    result = [reduced, add_one]
    return array(result)


@pytest.fixture
def mynetwork() -> Network:
    """Testing fixture for a feature."""
    from flowlayer.core.network import Network

    network = Network("my-network", outputs=[my_out])
    return network
