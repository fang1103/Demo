from __future__ import annotations

from dataclasses import dataclass

from .ontology import OntologyDataset
from .operations import NetworkOperationalModel, resilience_curve
from .optimization import Action, prioritize_actions
from .simulation import FailureScenario, simulate_cascading_failures


@dataclass(slots=True)
class PipelineInputs:
    failed_assets: list[str]
    degradation_rate: float
    dependency_threshold: float
    max_steps: int
    coupling_mode: str
    optimization_strategy: str
    budget: float


@dataclass(slots=True)
class PipelineOutput:
    simulation_history: dict[str, list[str]]
    resilience_points: list[dict[str, float]]
    selected_actions: list[Action]
    service_ratio: float
    health_index: float


def run_operational_pipeline(
    dataset: OntologyDataset,
    actions_catalog: list[Action],
    inputs: PipelineInputs,
    prefer_networkx: bool = True,
) -> PipelineOutput:
    graph = dataset.to_graph(prefer_networkx=prefer_networkx)

    scenario = FailureScenario(
        failed_nodes=inputs.failed_assets,
        degradation_rate=inputs.degradation_rate,
        dependency_threshold=inputs.dependency_threshold,
        max_steps=inputs.max_steps,
        coupling_mode=inputs.coupling_mode,
    )
    history = simulate_cascading_failures(graph.copy(), scenario)
    curve = resilience_curve(history, graph.copy())

    model = NetworkOperationalModel()
    for step_failures in history.values():
        for node in step_failures:
            if node in graph.nodes:
                graph.nodes[node]["condition"] = 0.0

    chosen_actions = prioritize_actions(actions_catalog, budget=inputs.budget, strategy=inputs.optimization_strategy)

    return PipelineOutput(
        simulation_history=history,
        resilience_points=curve,
        selected_actions=chosen_actions,
        service_ratio=model.service_ratio(graph),
        health_index=model.network_health_index(graph),
    )
