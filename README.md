# Multimodal Infrastructure Resilience Demo

This repository provides a modular Python prototype for studying cascading failures across interdependent infrastructure systems (gas, power, telecom, etc.) and testing resilience improvement actions.

## Foundry-inspired architecture

The demo is structured similarly to Palantir Foundry workflows:

1. **Ontology Layer**
   - `OntologyObject` and `OntologyLink` define typed entities and relationships.
   - `OntologyDataset` behaves like a curated ontology-backed dataset.
2. **Pipeline Layer**
   - `run_operational_pipeline(...)` is the orchestration transform that executes scenario simulation, resilience calculations, and decision optimization.
3. **Application Layer**
   - `app.py` is the interactive operational application consuming pipeline outputs.
4. **Decision Layer**
   - Optimization strategies (`greedy`, `exact`) mimic pluggable decision engines.

## Modules

- `src/multimodal_demo/ontology.py`
  - Foundry-like ontology model + demo dataset
- `src/multimodal_demo/pipeline.py`
  - End-to-end orchestration pipeline
- `src/multimodal_demo/application.py`
  - Demo dataset/action-catalog loaders
- `src/multimodal_demo/simulation.py`
  - Interdependency and cascading-failure models
- `src/multimodal_demo/operations.py`
  - Resilience and operational metrics
- `src/multimodal_demo/optimization.py`
  - Decision optimization strategies
- `src/multimodal_demo/graph.py`
  - Graph backend abstraction (NetworkX + fallback)

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
