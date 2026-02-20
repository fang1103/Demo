from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .graph import GraphBackend, build_graph_backend


@dataclass(slots=True)
class OntologyObject:
    """Foundry-like object representing a typed entity in the operational ontology."""

    rid: str
    object_type: str
    domain: str
    name: str
    latitude: float
    longitude: float
    condition: float = 1.0
    capacity: float = 1.0
    demand: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class OntologyLink:
    source_rid: str
    target_rid: str
    link_type: str
    weight: float = 1.0
    directed: bool = True
    coupling_model: str = "linear"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class OntologyDataset:
    objects: dict[str, OntologyObject] = field(default_factory=dict)
    links: list[OntologyLink] = field(default_factory=list)

    def add_object(self, obj: OntologyObject) -> None:
        self.objects[obj.rid] = obj

    def add_link(self, link: OntologyLink) -> None:
        if link.source_rid not in self.objects or link.target_rid not in self.objects:
            raise ValueError("Ontology link endpoints must already exist in objects.")
        self.links.append(link)

    def to_graph(self, prefer_networkx: bool = True) -> GraphBackend:
        graph = build_graph_backend(prefer_networkx=prefer_networkx)

        for obj in self.objects.values():
            graph.add_node(
                obj.rid,
                object_type=obj.object_type,
                domain=obj.domain,
                name=obj.name,
                latitude=obj.latitude,
                longitude=obj.longitude,
                condition=obj.condition,
                capacity=obj.capacity,
                demand=obj.demand,
                **obj.metadata,
            )

        for link in self.links:
            attrs = {
                "link_type": link.link_type,
                "weight": link.weight,
                "directed": link.directed,
                "coupling_model": link.coupling_model,
                **link.metadata,
            }
            graph.add_edge(link.source_rid, link.target_rid, **attrs)
            if not link.directed:
                graph.add_edge(link.target_rid, link.source_rid, **attrs)

        return graph


def build_demo_ontology() -> OntologyDataset:
    dataset = OntologyDataset()
    dataset.add_object(OntologyObject("gas_supply_1", "GasSupply", "gas", "Gas Supply", 29.7604, -95.3698, capacity=120))
    dataset.add_object(OntologyObject("compressor_1", "Compressor", "gas", "Compressor", 29.9, -95.2, capacity=100))
    dataset.add_object(OntologyObject("plant_1", "Generator", "power", "Gas Power Plant", 30.0, -95.0, capacity=80))
    dataset.add_object(OntologyObject("substation_1", "Substation", "power", "Substation", 30.1, -94.9, demand=60))
    dataset.add_object(OntologyObject("telecom_1", "Relay", "telecom", "Telecom Relay", 30.12, -94.85, demand=20))

    dataset.add_link(OntologyLink("gas_supply_1", "compressor_1", "pipeline", weight=0.9, directed=False))
    dataset.add_link(OntologyLink("compressor_1", "plant_1", "fuel_supply", weight=0.95, coupling_model="threshold"))
    dataset.add_link(OntologyLink("plant_1", "substation_1", "transmission", weight=0.9))
    dataset.add_link(OntologyLink("substation_1", "telecom_1", "power_supply", weight=0.8))

    return dataset
