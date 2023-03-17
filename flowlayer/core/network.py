import inspect
import zlib
from typing import Any, Callable, Dict, Generic, List, Optional, Set, Tuple, Type, TypeVar, Union

import numpy
from networkx import MultiDiGraph
from networkx.algorithms.dag import descendants
from networkx.algorithms.traversal.breadth_first_search import bfs_edges

from ilflow.core.api import EngineAPI, FeatureStoreAPI, NetworkAPI, NetworkPlotAPI
from ilflow.core.engine import SerialEngine
from ilflow.core.nodes import DataNode, GearInput, GearInputOutput, GearNode, GearOutput, NetworkNode, OutputNode

T = TypeVar("T")
Maybe = Union[Any, T]


class Depends(Generic[T]):
    """Express gear input dependency."""

    def __init__(self, func: Callable[..., Any]) -> None:
        """Constructor for dependency edge."""
        from datagears.core.nodes import GearNode

        self._func: Callable[..., Any] = func
        self._gear = GearNode(self._func)

    @property
    def gear(self) -> GearNode:
        """Return function dependencies as a gear."""
        return self._gear


class NetworkPropertyMixin(NetworkAPI):
    """Network property mixin."""

    def __init__(self, name: str, version: str, graph: MultiDiGraph) -> None:
        """Network property mixin."""
        self._name = name
        self._version = version

        self._graph = graph

    def __repr__(self) -> str:
        """String representation."""
        return f"{self._name}-{self._version}"

    @property
    def name(self) -> str:
        """Name of the feature."""
        return self._name

    @property
    def version(self) -> str:
        """Version of the feature."""
        return self._version

    @property
    def identifier(self) -> int:
        """Identifier containing name and version."""
        _id: int = zlib.crc32(bytes(f"{self._name}-{self._version}", "utf-8"))
        return _id

    @property
    def graph(self) -> MultiDiGraph:
        """Get computational graph representation."""
        return self._graph

    @property
    def plot(self) -> NetworkPlotAPI:
        """Plot the network."""
        from datagears.core.plot import NetworkPlot

        return NetworkPlot(self._graph)

    @property
    def roots(self) -> List[GearNode]:
        """Calculate ranks of gears in a network."""

        def check_predecessors(node: NetworkNode) -> bool:
            """Checks predecessors of a node."""
            if not isinstance(node, GearNode):
                return False

            all_inputs = [True if isinstance(p, GearInput) else False for p in self._graph.predecessors(node)]  # type: ignore

            return all(all_inputs) or not all_inputs

        roots: List[GearNode] = [
            node
            for node in self._graph.nodes  # type: ignore
            if check_predecessors(node)  # type: ignore
        ]

        return roots

    @property
    def input_shape(self) -> Dict[str, Type[Any]]:
        """Returns input shape of the computational graph."""
        inputs: Dict[str, Type[Any]] = {node.name: node.annotation for node in self._graph.nodes if isinstance(node, GearInput)}  # type: ignore

        return inputs

    @property
    def inputs(self) -> List[GearInput]:
        """Return all inputs with values of a graph."""
        inputs: List[GearInput] = [node for node in self._graph.nodes if isinstance(node, GearInput)]  # type: ignore

        return inputs

    @property
    def outputs(self) -> List[OutputNode]:
        """Return all outputs of a graph."""
        outputs: List[OutputNode] = [node for node in self._graph.nodes if isinstance(node, GearInputOutput) or isinstance(node, GearOutput)]  # type: ignore

        return outputs


class Network(NetworkPropertyMixin):
    """Representation of a DAG which contains all processing data."""

    def __init__(
        self,
        name: str,
        outputs: Optional[List[Callable[..., numpy.ndarray]]] = None,
        version: str = "0.1.0",
        engine: Optional[EngineAPI] = None,
        feature_store: Optional[FeatureStoreAPI] = None,
    ) -> None:
        """Network constructor."""
        self._outputting_nodes = outputs or []
        self._graph: MultiDiGraph = MultiDiGraph(name=name)
        self._feature_store = feature_store

        self._last_results: List[Tuple[str, str]]

        for output in self._outputting_nodes:
            gear = GearNode(output, graph=self._graph)
            self._attach_output(gear, graph_output=True)
            self._add_gear(gear)

        if engine is None:
            self._engine = SerialEngine()

        super().__init__(name, version, self._graph)

    def _attach_input(self, param: inspect.Parameter, dst: GearNode) -> None:
        """Attach input to the gear."""
        value = param.default if param.default != param.empty else None
        annotation = param.annotation if param.annotation != param.empty else Any

        gear_input = GearInput(param.name, value, annotation, graph=self._graph)
        self._graph.add_edge(gear_input, dst)  # type: ignore

    def _attach_output(self, src_gear: GearNode, name: Optional[str] = None, graph_output: bool = False) -> OutputNode:
        """Attach output to the gear."""
        if not name:
            name = f"{str(src_gear)}"

        src_gear_output: OutputNode
        if graph_output:
            src_gear_output = GearOutput(name, None, src_gear.output_type, graph=self._graph)
        else:
            src_gear_output = GearInputOutput(name, None, src_gear.output_type, graph=self._graph)

        self._graph.add_edge(src_gear, src_gear_output)  # type: ignore
        return src_gear_output

    def _add_gear(self, gear: GearNode) -> None:
        """Add gear to the graph."""
        gear.set_graph(self._graph)

        for name, param in gear.params.items():
            if param.default and isinstance(param.default, Depends):
                src_gear = param.default.gear
                src_gear_output = self._attach_output(src_gear, name=name)
                self._graph.add_edge(src_gear_output, gear)  # type: ignore
                self._add_gear(src_gear)
            else:
                self._attach_input(param, gear)

    def compute_next(self) -> List[OutputNode]:
        """Returns next nodes ready for evaluation."""
        # NOTE: Find all nodes of type `OutputNode`.
        outputs: Set[OutputNode] = {
            dst
            for r in self.roots
            for _, dst in bfs_edges(self._graph, r)  # type: ignore
            if (isinstance(dst, GearOutput) or isinstance(dst, GearInputOutput)) and dst.is_empty  # TODO: check for 'OutputNode'
        }

        # NOTE: For each `DataNode`, build set of descendants.
        reachable: Set[NetworkNode] = {node for output in outputs for node in descendants(self._graph, output)}  # type: ignore

        # NOTE: For each `DataNode`, exclude its connected descendant of the same type.
        result: List[OutputNode] = [node for node in outputs if node not in reachable]

        return result

    def copy(self, name: Optional[str] = None, version: Optional[str] = None) -> "Network":
        """Create a copy of an `Network` instance."""
        _version = version or self._version
        _name = name or self._name

        return Network(_name, outputs=self._outputting_nodes, version=_version, feature_store=self._feature_store)  # type: ignore

    def set_input(self, input_data: Dict[str, Any]) -> None:
        """Set input data for the graph computation."""
        if input_data.keys() != self.input_shape.keys():
            raise ValueError("input data is wrong format - check `network.input_shape`")

        inputs: Dict[str, DataNode] = {node.name: node for node in self._graph.nodes if isinstance(node, GearInput)}  # type: ignore

        for name, value in input_data.items():
            inputs[name].set_value(value)

    @property
    def results(self) -> List[GearOutput]:
        """Return results of the feature data flow."""
        _results: List[GearOutput] = [output_node for output_node in self.outputs if isinstance(output_node, GearOutput) and self.name in str(output_node)]

        return _results

    def run(self, **kwargs: Any) -> NetworkAPI:
        """Compute all data nodes of the network."""
        if self._engine is None:
            raise ValueError("engine not running")

        if not self._engine.is_ready():
            self._engine.setup()

        network_run = self._engine.execute(self.copy(), **kwargs)

        if self._feature_store is not None:
            self._last_results = [self._feature_store.set(out.value, network_run) for out in network_run.results]

        return network_run
