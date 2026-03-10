from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class GraphBackend(Protocol):
    def add_node(self, node: str, **attrs: Any) -> None: ...
    def add_edge(self, source: str, target: str, **attrs: Any) -> None: ...
    def predecessors(self, node: str) -> list[str]: ...
    def get_edge_data(self, source: str, target: str) -> dict[str, Any] | None: ...
    def number_of_nodes(self) -> int: ...
    def copy(self) -> GraphBackend: ...

    @property
    def nodes(self) -> Any: ...


class SimpleDiGraph:
    """Fallback graph implementation used when NetworkX is unavailable."""

    def __init__(self) -> None:
        self._nodes: dict[str, dict[str, Any]] = {}
        self._edges: dict[tuple[str, str], dict[str, Any]] = {}

    def add_node(self, node: str, **attrs: Any) -> None:
        self._nodes[node] = attrs

    def add_edge(self, source: str, target: str, **attrs: Any) -> None:
        self._edges[(source, target)] = attrs

    @property
    def nodes(self) -> "NodeView":
        return NodeView(self)

    def predecessors(self, node: str) -> list[str]:
        return [src for (src, dst) in self._edges if dst == node]

    def get_edge_data(self, source: str, target: str) -> dict[str, Any] | None:
        return self._edges.get((source, target))

    def number_of_nodes(self) -> int:
        return len(self._nodes)

    def copy(self) -> "SimpleDiGraph":
        g = SimpleDiGraph()
        g._nodes = {k: v.copy() for k, v in self._nodes.items()}
        g._edges = {k: v.copy() for k, v in self._edges.items()}
        return g


class NodeView:
    def __init__(self, graph: SimpleDiGraph) -> None:
        self._graph = graph

    def __iter__(self):
        return iter(self._graph._nodes.keys())

    def __contains__(self, item: str) -> bool:
        return item in self._graph._nodes

    def __getitem__(self, key: str) -> dict[str, Any]:
        return self._graph._nodes[key]

    def __call__(self, data: bool = False):
        if data:
            return list(self._graph._nodes.items())
        return list(self._graph._nodes.keys())


@dataclass(slots=True)
class NetworkXAdapter:
    """Adapter wrapper to provide a stable GraphBackend interface."""

    graph: Any

    def add_node(self, node: str, **attrs: Any) -> None:
        self.graph.add_node(node, **attrs)

    def add_edge(self, source: str, target: str, **attrs: Any) -> None:
        self.graph.add_edge(source, target, **attrs)

    @property
    def nodes(self) -> Any:
        return self.graph.nodes

    def predecessors(self, node: str) -> list[str]:
        return list(self.graph.predecessors(node))

    def get_edge_data(self, source: str, target: str) -> dict[str, Any] | None:
        return self.graph.get_edge_data(source, target)

    def number_of_nodes(self) -> int:
        return self.graph.number_of_nodes()

    def copy(self) -> "NetworkXAdapter":
        return NetworkXAdapter(self.graph.copy())


def build_graph_backend(prefer_networkx: bool = True) -> GraphBackend:
    if prefer_networkx:
        try:
            import networkx as nx

            return NetworkXAdapter(nx.DiGraph())
        except ModuleNotFoundError:
            pass
    return SimpleDiGraph()
