from __future__ import annotations

"""Backward-compatible schema aliases to the ontology layer."""

from .ontology import OntologyDataset, OntologyLink, OntologyObject, build_demo_ontology

AssetNode = OntologyObject
RelationshipEdge = OntologyLink
UnifiedNetwork = OntologyDataset


def build_demo_network() -> UnifiedNetwork:
    return build_demo_ontology()
