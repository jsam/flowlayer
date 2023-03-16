import pytest

from datagears.core.engine import DaskEngine, PoolEngine, SerialEngine
from datagears.core.network import Network
from datagears.core.nodes import GearNode, InvalidGraph, OutputNode
from tests.fixtures import Fixture


class TestSerialEngine:
    """Check all aspects of SerialEngine implementation."""

    def test_construction(self, myfeature: Fixture[Network]) -> None:
        """Test serial engine."""
        mynet: Network = myfeature
        engine = SerialEngine()

        assert engine.is_ready()
        engine.setup()
        assert engine.is_ready()

        new_net = engine.execute(mynet, a=5, b=20, c1=30)
        engine.teardown()

        assert new_net is not None
        assert new_net.outputs
        for output_node in new_net.outputs:
            assert output_node.value is not None

    def test_partial_construction(self, myfeature: Fixture[Network]) -> None:
        """Test SerialEngine partial construction."""
        mynet: Network = myfeature
        engine = SerialEngine()

        with pytest.raises(ValueError):
            _ = engine.execute(None, a=3, b=2, c=10)  # type: ignore

        dst: OutputNode = mynet.outputs[-1]
        another_gear = GearNode(lambda x: x ** 2)
        mynet.graph.add_edge(another_gear, dst)  # type: ignore

        with pytest.raises(InvalidGraph) as exp:
            _ = engine.execute(mynet, a=5, b=20, c1=30)

        assert exp.value.msg == "found a data node produced by multiple gears: [add_one, <lambda>]"
        assert "gears" in exp.value.params.keys()

    def test_submit_next_execution(self, myfeature: Fixture[Network]) -> None:
        """Check execution sequence."""
        mynet: Network = myfeature.copy()
        engine = SerialEngine()

        mynet.set_input({"a": 1, "b": 3, "c1": 10})

        engine._network = mynet  # type: ignore
        result = engine._submit_next()  # type: ignore
        assert result is True

        engine._network = None  # type: ignore
        with pytest.raises(ValueError):
            engine._submit_next()  # type: ignore


class TestPoolEngine:
    """Check all aspects of PoolEngine implementation."""

    def test_construction(self, myfeature: Fixture[Network]) -> None:
        """Test serial engine."""
        mynet: Network = myfeature
        engine = PoolEngine()

        assert engine.is_ready() is False
        engine.setup()
        assert engine.is_ready() is True

        new_net = engine.execute(mynet, a=5, b=20, c1=30)
        engine.teardown()

        assert new_net is not None
        assert new_net.outputs
        for output_node in new_net.outputs:
            assert output_node.value is not None

    def test_partial_construction(self, myfeature: Fixture[Network]) -> None:
        """Test SerialEngine partial construction."""
        mynet: Network = myfeature
        engine = PoolEngine()
        engine.setup()

        with pytest.raises(ValueError):
            _ = engine.execute(None, a=3, b=2, c=10)  # type: ignore

        dst: OutputNode = mynet.outputs[-1]
        another_gear = GearNode(lambda x: x ** 2)
        mynet.graph.add_edge(another_gear, dst)  # type: ignore

        with pytest.raises(InvalidGraph) as exp:
            _ = engine.execute(mynet, a=5, b=20, c1=30)

        assert exp.value.msg == "found a data node produced by multiple gears: [add_one, <lambda>]"
        assert "gears" in exp.value.params.keys()

    def test_submit_next_execution(self, myfeature: Fixture[Network]) -> None:
        """Check execution sequence."""
        mynet: Network = myfeature.copy()
        engine = PoolEngine()
        engine.setup()

        mynet.set_input({"a": 1, "b": 3, "c1": 10})

        engine._network = mynet  # type: ignore
        result = engine._submit_next()  # type: ignore
        assert set(result)

        engine._executor = None  # type: ignore
        with pytest.raises(ValueError):
            engine._submit_next()  # type: ignore

        engine._network = None  # type: ignore
        with pytest.raises(ValueError):
            engine._submit_next()  # type: ignore

    def test_teardown(self) -> None:
        """Check teardown step."""
        engine = PoolEngine()

        with pytest.raises(NotImplementedError):
            engine.register()

        with pytest.raises(ValueError):
            engine.teardown()

        engine.setup()
        engine.teardown()


class TestDaskEngine:
    """Check all aspects of DaskEngine implementation."""

    engine: DaskEngine

    @classmethod
    def setup_class(cls) -> None:
        """Setup engine for all tests."""
        pass

    @classmethod
    def teardown_class(cls) -> None:
        """Teardown engine."""
        pass

    def test_dask_install(self, dask_engine: DaskEngine) -> None:
        """Test dask install."""
        import os
        from unittest.mock import Mock

        mock = Mock()
        os.system = mock

        dask_engine.dask_install(os, ["networkx", "numpy"])  # type: ignore
        mock.assert_called()

    def test_dask_execution(self, myfeature: Fixture[Network], dask_engine: DaskEngine) -> None:
        """Test dask engine."""
        # NOTE: Test network construction.
        mynet: Network = myfeature.copy()
        assert dask_engine.is_ready() is True

        new_net = dask_engine.execute(mynet, a=5, b=20, c1=30)

        assert new_net is not None
        assert new_net.outputs
        for output_node in new_net.outputs:
            assert output_node.value is not None

        # NOTE: Test exception raise in case of provided network is None
        with pytest.raises(ValueError):
            _ = dask_engine.execute(None, a=3, b=2, c=10)  # type: ignore

        # NOTE: Test exception raised in case executor not set.
        _exec = dask_engine._executor  # type: ignore
        dask_engine._executor = None  # type: ignore
        with pytest.raises(ValueError):
            _ = dask_engine.execute(mynet, a=3, b=2, c=10)
        dask_engine._executor = _exec  # type: ignore

        # NOTE: Test InvalidGraph structure.
        mynet = myfeature.copy()
        dst: OutputNode = mynet.outputs[-1]
        another_gear = GearNode(lambda x: x ** 2)
        mynet.graph.add_edge(another_gear, dst)  # type: ignore

        with pytest.raises(InvalidGraph) as exp:
            _ = dask_engine.execute(mynet, a=5, b=20, c1=30)

        assert exp.value.msg == "found a data node produced by multiple gears: [add_one, <lambda>]"
        assert "gears" in exp.value.params.keys()

        # NOTE: Test execution sequence.
        mynet = myfeature.copy()
        mynet.set_input({"a": 1, "b": 3, "c1": 10})

        dask_engine._network = mynet  # type: ignore
        result = dask_engine._submit_next()  # type: ignore
        assert result is True

        # NOTE: Test exception raised in case of not set executor.
        _exec = dask_engine._executor  # type: ignore
        dask_engine._executor = None  # type: ignore
        with pytest.raises(ValueError):
            dask_engine._submit_next()  # type: ignore
        dask_engine._executor = _exec  # type: ignore

        # NOTE: Test exception raised in case of not set network.
        _net = dask_engine._network  # type: ignore
        dask_engine._network = None  # type: ignore
        with pytest.raises(ValueError):
            dask_engine._submit_next()  # type: ignore
        dask_engine._network = _net  # type: ignore
