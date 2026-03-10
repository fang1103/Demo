from __future__ import annotations

from dataclasses import dataclass

from .graph import GraphBackend


@dataclass(slots=True)
class NetworkOperationalModel:
    service_threshold: float = 0.5

    def service_ratio(self, graph: GraphBackend) -> float:
        eligible = [node for node in graph.nodes if graph.nodes[node].get("demand", 0.0) > 0]
        if not eligible:
            return 1.0
        served = [node for node in eligible if graph.nodes[node].get("condition", 1.0) >= self.service_threshold]
        return len(served) / len(eligible)

    def network_health_index(self, graph: GraphBackend) -> float:
        if graph.number_of_nodes() == 0:
            return 0.0
        return sum(float(graph.nodes[node].get("condition", 1.0)) for node in graph.nodes) / graph.number_of_nodes()


def resilience_curve(simulation_history: dict[str, list[str]], base_graph: GraphBackend) -> list[dict[str, float]]:
    working_graph = base_graph.copy()
    model = NetworkOperationalModel()
    output: list[dict[str, float]] = []

    for step, failed_nodes in simulation_history.items():
        for node in failed_nodes:
            if node in working_graph.nodes:
                working_graph.nodes[node]["condition"] = 0.0

        output.append(
            {
                "step": int(step.split("_")[1]),
                "service_ratio": model.service_ratio(working_graph),
                "health_index": model.network_health_index(working_graph),
            }
        )

    return sorted(output, key=lambda x: x["step"])
