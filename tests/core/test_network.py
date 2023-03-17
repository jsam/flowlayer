import pytest
from numpy import array, ndarray

from flowlayer.core.network import Network
from flowlayer.core.nodes import GearNode
from tests.fixtures.core.generics import Fixture


def test_network_construction(mynetwork: Fixture[Network]) -> None:
    """Test network construction."""

    network: Network = mynetwork
    graph = network.graph

    assert graph
    assert list(network.graph.nodes)
    assert list(network.graph.edges)

    plot = network.plot
    assert plot
    assert plot.meta

    assert network.name
    assert network.version
    assert str(network) == "my-network-0.1.0"

    assert network.roots
    for gear in network.roots:
        assert isinstance(gear, GearNode)
        assert str(gear) in {"add", "add_one"}

    assert network.input_shape == {"c1": int, "b": int, "a": int}

    expected_inputs = [
        "reduce(c1[int] = None, ...)",
        "add(a[int] = None, ...)",
        "add(b[int] = 10, ...)",
    ]
    assert network.inputs
    for input_node in network.inputs:
        assert str(input_node) in expected_inputs

    expected_outputs = [
        "my-network(my_out[ndarray] = None)",
        "my_out(reduced[int] = None, ...)",
        "reduce(sum[int] = None, ...)",
        "my_out(add_one[int] = None, ...)",
    ]
    assert network.outputs
    for output_node in network.outputs:
        assert str(output_node) in expected_outputs


def test_network_set_input(mynetwork: Fixture[Network]) -> None:
    """Test network set input."""
    network: Network = mynetwork

    with pytest.raises(ValueError):
        network.set_input({})

    # TODO: Fix this.
    # default_values = {"a": None, "b": 10, "c": None}
    # assert network.inputs == default_values

    new_values = {"a": 1, "b": 2, "c1": 3}
    network.set_input(new_values)
    # assert network.inputs == new_values

    for input_node in network.inputs:
        assert new_values[input_node.name] == input_node.value


def test_network_run(mynetwork: Fixture[Network]) -> None:
    """Test network run."""
    network: Network = mynetwork

    assert network.input_shape == {"c1": int, "a": int, "b": int}
    assert network.output_shape == {"my_out": ndarray}

    result = network.run(a=1, b=3, c1=10)
    assert result

    output = {out.name: out.value for out in result.outputs}
    expected = {"my_out": array([-6, 1]), "reduced": -6, "sum": 4, "add_one": 1}

    assert str(output) == str(expected)

    assert all([result.name in str(r) for r in result.results])

    network._engine = None  # type: ignore
    with pytest.raises(ValueError):
        _ = network.run(a=1, b=3, c1=10)

    from unittest.mock import Mock

    network._engine = Mock()  # type: ignore
    network._engine.is_ready = lambda: False  # type: ignore
    network._engine.run = lambda _1, **_2: {}  # type: ignore

    _ = network.run(a=1, b=3, c1=10)
    network._engine.setup.assert_called_once_with()  # type: ignore
