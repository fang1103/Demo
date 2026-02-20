from __future__ import annotations

from .ontology import OntologyDataset, build_demo_ontology
from .optimization import Action


def load_demo_dataset() -> OntologyDataset:
    return build_demo_ontology()


def load_action_catalog() -> list[Action]:
    return [
        Action("Install compressor redundancy", cost=80, impact_score=65, phase="design"),
        Action("Upgrade pipeline segment", cost=55, impact_score=40, phase="expansion"),
        Action("Deploy mobile generators", cost=45, impact_score=52, phase="response"),
        Action("Emergency telecom backup", cost=35, impact_score=34, phase="response"),
        Action("Accelerated repair crews", cost=60, impact_score=58, phase="recovery"),
    ]
