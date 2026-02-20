from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .graph import GraphBackend


class CouplingModel(Protocol):
    def impact(self, source_condition: float, weight: float, threshold: float) -> float: ...


@dataclass(slots=True)
class LinearCouplingModel:
    def impact(self, source_condition: float, weight: float, threshold: float) -> float:
        return (1.0 - source_condition) * weight


@dataclass(slots=True)
class ThresholdCouplingModel:
    def impact(self, source_condition: float, weight: float, threshold: float) -> float:
        return weight if source_condition <= threshold else 0.0


@dataclass(slots=True)
class FailureScenario:
    failed_nodes: list[str]
    degradation_rate: float = 0.35
    dependency_threshold: float = 0.4
    max_steps: int = 5
    coupling_mode: str = "linear"


def _build_model(name: str) -> CouplingModel:
    if name == "threshold":
        return ThresholdCouplingModel()
    return LinearCouplingModel()


def simulate_cascading_failures(graph: GraphBackend, scenario: FailureScenario) -> dict[str, list[str]]:
    failures_by_step: dict[str, list[str]] = {"step_0": list(scenario.failed_nodes)}
    model = _build_model(scenario.coupling_mode)

    for node in graph.nodes:
        graph.nodes[node].setdefault("condition", 1.0)

    for node in scenario.failed_nodes:
        if node in graph.nodes:
            graph.nodes[node]["condition"] = 0.0

    already_failed = set(scenario.failed_nodes)

    for step in range(1, scenario.max_steps + 1):
        new_failures: list[str] = []

        for node in list(graph.nodes):
            if node in already_failed:
                continue

            predecessors = graph.predecessors(node)
            if not predecessors:
                continue

            influence_score = 0.0
            total_weight = 0.0

            for pred in predecessors:
                edge_data = graph.get_edge_data(pred, node) or {}
                weight = float(edge_data.get("weight", 1.0))
                pred_condition = float(graph.nodes[pred].get("condition", 1.0))
                influence_score += model.impact(pred_condition, weight, scenario.dependency_threshold)
                total_weight += weight

            normalized_impact = influence_score / total_weight if total_weight > 0 else 0.0
            graph.nodes[node]["condition"] = max(0.0, float(graph.nodes[node]["condition"]) - normalized_impact * scenario.degradation_rate)

            if graph.nodes[node]["condition"] <= scenario.dependency_threshold:
                new_failures.append(node)

        if not new_failures:
            break

        failures_by_step[f"step_{step}"] = new_failures
        already_failed.update(new_failures)
        for node in new_failures:
            graph.nodes[node]["condition"] = 0.0

    return failures_by_step
