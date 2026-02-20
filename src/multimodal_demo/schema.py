from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .graph import GraphBackend, build_graph_backend


@dataclass(slots=True)
class AssetNode:
    id: str
    network_type: str
    asset_type: str
    label: str
    latitude: float
    longitude: float
    condition: float = 1.0
    capacity: float = 1.0
    demand: float = 0.0
    repair_time_hours: float = 12.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RelationshipEdge:
    source: str
    target: str
    relation_type: str
    weight: float = 1.0
    directed: bool = True
    coupling_model: str = "linear"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class UnifiedNetwork:
    nodes: dict[str, AssetNode] = field(default_factory=dict)
    edges: list[RelationshipEdge] = field(default_factory=list)

    def add_node(self, node: AssetNode) -> None:
        self.nodes[node.id] = node

    def add_edge(self, edge: RelationshipEdge) -> None:
        if edge.source not in self.nodes or edge.target not in self.nodes:
            raise ValueError("Both edge endpoints must exist in network nodes.")
        self.edges.append(edge)

    def to_graph(self, prefer_networkx: bool = True) -> GraphBackend:
        graph = build_graph_backend(prefer_networkx=prefer_networkx)
        for node in self.nodes.values():
            graph.add_node(
                node.id,
                network_type=node.network_type,
                asset_type=node.asset_type,
                label=node.label,
                latitude=node.latitude,
                longitude=node.longitude,
                condition=node.condition,
                capacity=node.capacity,
                demand=node.demand,
                repair_time_hours=node.repair_time_hours,
                **node.metadata,
            )

        for edge in self.edges:
            edge_data = {
                "relation_type": edge.relation_type,
                "weight": edge.weight,
                "directed": edge.directed,
                "coupling_model": edge.coupling_model,
                **edge.metadata,
            }
            graph.add_edge(edge.source, edge.target, **edge_data)
            if not edge.directed:
                graph.add_edge(edge.target, edge.source, **edge_data)

        return graph


def build_demo_network() -> UnifiedNetwork:
    network = UnifiedNetwork()
    network.add_node(AssetNode("gas_supply_1", "gas", "supply", "Gas Supply", 29.7604, -95.3698, capacity=120))
    network.add_node(AssetNode("compressor_1", "gas", "compressor", "Compressor", 29.9, -95.2, capacity=100))
    network.add_node(AssetNode("plant_1", "power", "generator", "Gas Power Plant", 30.0, -95.0, capacity=80))
    network.add_node(AssetNode("substation_1", "power", "substation", "Substation", 30.1, -94.9, demand=60))
    network.add_node(AssetNode("telecom_1", "telecom", "relay", "Telecom Relay", 30.12, -94.85, demand=20))

    network.add_edge(RelationshipEdge("gas_supply_1", "compressor_1", "pipeline", weight=0.9, directed=False))
    network.add_edge(RelationshipEdge("compressor_1", "plant_1", "fuel_supply", weight=0.95, coupling_model="threshold"))
    network.add_edge(RelationshipEdge("plant_1", "substation_1", "transmission", weight=0.9))
    network.add_edge(RelationshipEdge("substation_1", "telecom_1", "power_supply", weight=0.8))

    return network
