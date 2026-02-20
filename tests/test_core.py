import unittest

from multimodal_demo.application import load_action_catalog, load_demo_dataset
from multimodal_demo.graph import SimpleDiGraph
from multimodal_demo.operations import NetworkOperationalModel, resilience_curve
from multimodal_demo.optimization import Action, prioritize_actions
from multimodal_demo.pipeline import PipelineInputs, run_operational_pipeline
from multimodal_demo.schema import build_demo_network
from multimodal_demo.simulation import FailureScenario, simulate_cascading_failures


class CoreDemoTests(unittest.TestCase):
    def test_cascading_failure_reaches_dependent_assets(self):
        graph = build_demo_network().to_graph(prefer_networkx=False)
        history = simulate_cascading_failures(
            graph,
            FailureScenario(failed_nodes=["compressor_1"], degradation_rate=1.0, dependency_threshold=0.5, max_steps=4),
        )
        flattened = {node for nodes in history.values() for node in nodes}
        self.assertIn("compressor_1", flattened)
        self.assertIn("plant_1", flattened)

    def test_threshold_mode_produces_failures(self):
        graph = build_demo_network().to_graph(prefer_networkx=False)
        history = simulate_cascading_failures(
            graph,
            FailureScenario(
                failed_nodes=["compressor_1"],
                degradation_rate=1.0,
                dependency_threshold=0.5,
                max_steps=4,
                coupling_mode="threshold",
            ),
        )
        flattened = {node for nodes in history.values() for node in nodes}
        self.assertIn("plant_1", flattened)

    def test_resilience_curve_monotonic_health(self):
        graph = build_demo_network().to_graph(prefer_networkx=False)
        history = {"step_0": ["compressor_1"], "step_1": ["plant_1"]}
        curve = resilience_curve(history, graph)
        self.assertGreaterEqual(curve[0]["health_index"], curve[1]["health_index"])

    def test_exact_action_prioritization(self):
        selected = prioritize_actions(
            [
                Action("A", cost=40, impact_score=40, phase="response"),
                Action("B", cost=50, impact_score=60, phase="recovery"),
                Action("C", cost=60, impact_score=90, phase="design"),
            ],
            budget=100,
            strategy="exact",
        )
        self.assertEqual({a.name for a in selected}, {"A", "C"})

    def test_service_ratio_bounds(self):
        graph = build_demo_network().to_graph(prefer_networkx=False)
        ratio = NetworkOperationalModel().service_ratio(graph)
        self.assertGreaterEqual(ratio, 0.0)
        self.assertLessEqual(ratio, 1.0)

    def test_simple_graph_copy(self):
        graph = SimpleDiGraph()
        graph.add_node("n1", condition=1.0)
        copied = graph.copy()
        copied.nodes["n1"]["condition"] = 0.0
        self.assertEqual(graph.nodes["n1"]["condition"], 1.0)

    def test_foundry_like_pipeline_orchestrates_end_to_end(self):
        output = run_operational_pipeline(
            dataset=load_demo_dataset(),
            actions_catalog=load_action_catalog(),
            inputs=PipelineInputs(
                failed_assets=["compressor_1"],
                degradation_rate=0.5,
                dependency_threshold=0.4,
                max_steps=5,
                coupling_mode="linear",
                optimization_strategy="greedy",
                budget=120,
            ),
            prefer_networkx=False,
        )
        self.assertTrue(output.resilience_points)
        self.assertGreaterEqual(output.service_ratio, 0.0)
        self.assertLessEqual(output.service_ratio, 1.0)


if __name__ == "__main__":
    unittest.main()
