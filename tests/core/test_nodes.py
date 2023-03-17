import inspect
import types
from inspect import Parameter
from typing import Any, Dict

import pytest
from numpy import ndarray


def test_simple_func_analysis() -> None:
    """Test function analysis."""
    from flowlayer.core.nodes import Signature
    from tests.fixtures import add

    sig = Signature(add)

    assert set(sig.params.keys()) == {"a", "b"}

    params = sig.params
    assert list(params.keys()) == ["a", "b"]
    assert params["a"] == Parameter("a", Parameter.POSITIONAL_OR_KEYWORD, annotation=int)
    assert params["b"] == Parameter("b", Parameter.POSITIONAL_OR_KEYWORD, annotation=int, default=10)

    assert sig.output_type == int


def test_depends_func_analysis() -> None:
    """Test function analysis with expressed dependency."""
    from flowlayer.core.network import Depends
    from flowlayer.core.nodes import Signature
    from tests.fixtures import reduce

    sig = Signature(reduce)

    assert set(sig.params.keys()) == {"c1", "sum"}
    assert sig.name == "reduce"
    assert reduce(3, 5) == 2

    params = sig.params
    assert params["c1"] == Parameter("c1", Parameter.POSITIONAL_OR_KEYWORD, annotation=int)

    assert "sum: Union[Any, int] = <datagears.core.network.Depends object at" in str(params["sum"])
    assert isinstance(params["sum"].default, Depends)
    assert isinstance(params["sum"].default._func, types.FunctionType)

    assert sig.output_type == int

    sig = Signature(params["sum"].default._func)
    assert set(sig.params.keys()) == {"a", "b"}

    params = sig.params
    assert params["a"] == inspect.Parameter("a", Parameter.POSITIONAL_OR_KEYWORD, annotation=int)
    assert params["b"] == inspect.Parameter("b", Parameter.POSITIONAL_OR_KEYWORD, annotation=int, default=10)
    assert sig.output_type == int


def test_gears_exception() -> None:
    """Check gears exception attributes."""
    from flowlayer.core.nodes import GearException, GearNode

    node = GearNode(lambda x: x)
    params: Dict[str, Any] = {}
    blank_exp = Exception()

    exp = GearException(node, params, blank_exp)

    assert exp
    assert exp.gear == node
    assert exp.params == params
    assert exp.raised_exception == blank_exp


def test_standalone_gear_node() -> None:
    """Check standalone gear node."""
    from flowlayer.core.nodes import GearNode

    gear_node = GearNode(lambda x: x + 1)

    assert gear_node.graph is None
    assert gear_node.name_unique == "gear_<lambda>"

    with pytest.raises(ValueError):
        gear_node.input_values


def test_graph_gear_node_exception() -> None:
    """Check standalone gear node exception handling."""
    from flowlayer.core.network import Network
    from flowlayer.core.nodes import GearException

    def f(p: int = 3) -> ndarray:
        raise KeyError

    mynet = Network("mynet", outputs=[f])
    assert mynet.roots

    gear_node = mynet.roots[0]
    with pytest.raises(GearException):
        gear_node()


def test_graph_gear_node() -> None:
    """Check gear node with associated graph."""
    from flowlayer.core.network import Network

    def f(p: int = 3) -> ndarray:
        return ndarray([p + 1])

    mynet = Network("mynet", outputs=[f])
    assert mynet.roots

    gear_node = mynet.roots[0]
    assert gear_node.graph == mynet.graph

    gear_node.set_graph(None)
    assert gear_node.graph is None

    gear_node.set_graph(mynet.graph)
    assert gear_node.graph == mynet.graph


def test_standalone_data_node() -> None:
    """Check standalone data node."""
    from flowlayer.core.nodes import DataNode

    data_node = DataNode("some_param", None, str)

    assert data_node.name == "some_param"
    assert data_node.name_unique == "some_param"
    assert data_node.value is None
    assert data_node.annotation == str

    assert str(data_node) == "some_param"
    assert data_node.is_empty is True

    with pytest.raises(TypeError):
        data_node.set_value(2)

    data_node.set_value("123")
    assert data_node.is_empty is False
    assert data_node.value == "123"


def test_graph_data_node() -> None:
    """Check data node with associated graph."""
    from numpy import ndarray

    from flowlayer.core.network import Network

    def f(p: int = 3) -> ndarray:
        return ndarray([p + 1])

    mynet = Network("mynet", outputs=[f])
    assert mynet.inputs

    data_node = mynet.inputs[0]
    assert data_node.graph == mynet.graph

    data_node.set_graph(None)
    assert data_node.graph is None

    data_node.set_graph(mynet.graph)
    assert data_node.graph == mynet.graph
