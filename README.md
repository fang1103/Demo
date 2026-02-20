# Multimodal Infrastructure Resilience Demo

This repository provides a modular Python prototype for studying cascading failures across interdependent infrastructure systems (gas, power, telecom, etc.) and testing resilience improvement actions.

## What is included

- **Unified network schema** for heterogeneous assets and relationships.
- **Graph backend abstraction** with automatic NetworkX usage when available and a local fallback for constrained environments.
- **Interdependency simulation** with pluggable coupling logic (`linear` and `threshold`).
- **Operational model hooks** for service and health metrics.
- **Interactive GIS dashboard** (Streamlit + Pydeck + Plotly).
- **Decision layer** with both greedy and exact budget-constrained action prioritization.

## Architecture

- `src/multimodal_demo/schema.py`
  - Generic `AssetNode` / `RelationshipEdge`
  - `UnifiedNetwork` storage + backend export (`to_graph`)
  - `build_demo_network()` seed topology
- `src/multimodal_demo/graph.py`
  - `GraphBackend` protocol
  - `NetworkXAdapter` and `SimpleDiGraph` fallback
- `src/multimodal_demo/simulation.py`
  - `FailureScenario`
  - `LinearCouplingModel` and `ThresholdCouplingModel`
  - `simulate_cascading_failures()`
- `src/multimodal_demo/operations.py`
  - `NetworkOperationalModel`
  - `resilience_curve()`
- `src/multimodal_demo/optimization.py`
  - `Action`
  - `prioritize_actions()` with `greedy` and `exact`
- `app.py`
  - End-to-end interactive demo with model/optimizer selection

## Run locally

```bash
python -m pip install -e .
streamlit run app.py
```

If you do not install the package, use:

```bash
PYTHONPATH=src streamlit run app.py
```

## Tests

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```
