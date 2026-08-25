"""
Knowledge graph construction pipeline.

Flow:
    Structured demo data (locations/shelters/resources/agencies/hospitals)
        -> nodes + relationships (ground truth, always trusted)
    Documents
        -> text extraction -> chunking -> entity extraction
        -> relationship extraction -> normalization -> graph edges

Node ids are the *canonical entity name* (see entity_normalizer) so that
structured data and document-derived mentions merge into the same node
instead of creating duplicates.
"""
from __future__ import annotations

from pathlib import Path

from app.config import DOCUMENTS_DIR
from app.documents.parser import parse_document, UnsupportedFileTypeError
from app.graph.entity_normalizer import normalize
from app.graph.graph_store import graph_store
from app.graph.relation_extractor import extract_relations
from app.utils.demo_data import load_demo_scenario


def seed_structured_data(store=None):
    """Load the structured demo scenario (locations, shelters, resources,
    agencies, hospitals, incidents) directly into the graph as ground-truth
    nodes and relationships."""
    store = store or graph_store
    scenario = load_demo_scenario()

    disaster_name = scenario["disaster"]["type"]
    disaster_props = {k: v for k, v in scenario["disaster"].items() if k != "type"}
    store.add_node(disaster_name, "Disaster", **disaster_props)

    for loc in scenario["locations"]:
        store.add_node(loc["name"], "Location", affected_population=loc["affected_population"], district=loc["district"])
        store.add_edge(disaster_name, "AFFECTED", loc["name"])

    for shelter in scenario["shelters"]:
        store.add_node(
            shelter["name"], "Shelter",
            capacity=shelter["capacity"], occupied=shelter["occupied"],
            available_capacity=shelter["available_capacity"],
            drinking_water=shelter["drinking_water"], food_available=shelter["food_available"],
            medical_support=shelter["medical_support"], contact=shelter["contact"],
            facilities=shelter["facilities"],
        )
        store.add_edge(shelter["location_name"], "HAS_SHELTER", shelter["name"])
        store.add_edge(shelter["name"], "LOCATED_IN", shelter["location_name"])
        if shelter["drinking_water"]:
            store.add_edge(shelter["name"], "HAS_RESOURCE", "Drinking Water")
        if shelter["medical_support"]:
            store.add_edge(shelter["name"], "HAS_RESOURCE", "Medical Support")
        if shelter["food_available"]:
            store.add_edge(shelter["name"], "HAS_RESOURCE", "Food Packets")

    for res in scenario["resources"]:
        agency = next((a["name"] for a in scenario["agencies"] if a["id"] == res["responsible_agency_id"]), None)
        store.add_node(
            res["name"], "Resource",
            unit=res["unit"], available=res["available"], required=res["required"],
            shortage=max(0, res["required"] - res["available"]),
        )
        store.add_edge(disaster_name, "REQUIRES", res["name"])
        if agency:
            store.add_edge(agency, "SUPPLIES", res["name"])

    for agy in scenario["agencies"]:
        store.add_node(agy["name"], "Agency", operates_in=agy["operates_in"])
        for action in agy["responsible_for"]:
            store.add_node(action, "ResponseAction")
            store.add_edge(agy["name"], "RESPONSIBLE_FOR", action)
        store.add_edge(agy["name"], "OPERATES_IN", agy["operates_in"])
        store.add_edge(disaster_name, "REQUIRES_ACTION", agy["responsible_for"][0] if agy["responsible_for"] else "Coordination")

    for hos in scenario["hospitals"]:
        store.add_node(
            hos["name"], "Hospital",
            total_beds=hos["total_beds"], emergency_beds=hos["emergency_beds"],
            available_emergency_beds=hos["available_emergency_beds"], facilities=hos["facilities"],
        )
        store.add_edge(hos["name"], "LOCATED_IN", hos["location_name"])
        store.add_edge(hos["location_name"], "HAS_HOSPITAL", hos["name"])

    for inc in scenario["incidents"]:
        loc_name = next((l["name"] for l in scenario["locations"] if l["id"] == inc["location_id"]), inc["location_id"])
        incident_node = f"Incident {inc['id']}"
        store.add_node(
            incident_node, "Incident",
            date=inc["date"], disaster_type=inc["disaster_type"], severity=inc["severity"],
            population_affected=inc["population_affected"], notes=inc["notes"],
        )
        store.add_edge(incident_node, "OCCURRED_IN", loc_name)
        store.add_edge(disaster_name, "CAUSED", incident_node)

    return store


def ingest_document_into_graph(file_path: str | Path, store=None) -> dict:
    """Parse a document, extract relationships, and merge them into the graph.
    Returns a small ingestion summary."""
    store = store or graph_store
    parsed = parse_document(file_path)
    relations = extract_relations(parsed.full_text)

    added = 0
    for rel in relations:
        if not rel.subject or not rel.obj:
            continue
        # Ensure nodes exist (typed as "Entity" if not already known elsewhere).
        if store.get_node(rel.subject) is None:
            store.add_node(rel.subject, "Entity", source_document=parsed.document_name)
        if store.get_node(rel.obj) is None:
            store.add_node(rel.obj, "Entity", source_document=parsed.document_name)
        store.add_edge(rel.subject, rel.predicate, rel.obj, evidence=rel.evidence, source_document=parsed.document_name)
        added += 1

    return {
        "document_name": parsed.document_name,
        "relations_extracted": len(relations),
        "edges_added": added,
    }


def rebuild_full_graph(store=None) -> dict:
    """Clear and rebuild the entire knowledge graph from structured demo data
    plus every document currently in the documents directory."""
    store = store or graph_store
    store.clear()
    seed_structured_data(store)

    ingested = []
    for path in sorted(DOCUMENTS_DIR.iterdir()):
        if path.suffix.lower() not in (".pdf", ".docx", ".txt", ".md"):
            continue
        try:
            ingested.append(ingest_document_into_graph(path, store))
        except UnsupportedFileTypeError:
            continue
        except Exception as exc:  # never let one bad document break the whole build
            ingested.append({"document_name": path.name, "error": str(exc)})

    return {
        "backend": store.backend_name,
        "node_count": store.node_count(),
        "edge_count": store.edge_count(),
        "documents_ingested": ingested,
    }
