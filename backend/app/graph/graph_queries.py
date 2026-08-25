"""
Reusable graph queries.

Each function here has a docstring showing the equivalent Cypher query for
documentation / viva purposes, and an implementation against the
`graph_store` interface (works identically whether the active backend is
Neo4j or the in-memory networkx fallback).
"""
from __future__ import annotations

from app.graph.graph_store import graph_store


def find_shelters_near_area(area_name: str, store=None) -> list[dict]:
    """
    Cypher:
        MATCH (l:Entity {id: $area})-[:HAS_SHELTER]->(s:Entity)
        RETURN s

    Also considers the disaster's district-wide shelters if the area itself
    doesn't directly list any.
    """
    store = store or graph_store
    neighbors = store.get_neighbors(area_name, relation="HAS_SHELTER", direction="out")
    return [n["node"] for n in neighbors]


def find_available_resources(min_shortage: int | None = None, store=None) -> list[dict]:
    """
    Cypher:
        MATCH (d:Entity {type:'Disaster'})-[:REQUIRES]->(r:Entity {type:'Resource'})
        RETURN r
    """
    store = store or graph_store
    resources = store.find_nodes(node_type="Resource")
    if min_shortage is not None:
        resources = [r for r in resources if r.get("shortage", 0) >= min_shortage]
    return resources


def find_hospitals_with_beds(min_available_beds: int = 1, store=None) -> list[dict]:
    """
    Cypher:
        MATCH (h:Entity {type:'Hospital'})
        WHERE h.available_emergency_beds >= $min
        RETURN h
    """
    store = store or graph_store
    hospitals = store.find_nodes(node_type="Hospital")
    return [h for h in hospitals if h.get("available_emergency_beds", 0) >= min_available_beds]


def find_agencies_for_action(action_name: str, store=None) -> list[dict]:
    """
    Cypher:
        MATCH (a:Entity {type:'Agency'})-[:RESPONSIBLE_FOR]->(action:Entity {id: $action})
        RETURN a
    """
    store = store or graph_store
    neighbors = store.get_neighbors(action_name, relation="RESPONSIBLE_FOR", direction="in")
    return [n["node"] for n in neighbors]


def find_affected_population(area_name: str, store=None) -> int | None:
    """
    Cypher:
        MATCH (l:Entity {id: $area})
        RETURN l.affected_population
    """
    store = store or graph_store
    node = store.get_node(area_name)
    return node.get("affected_population") if node else None


def find_connected_entities(entity_name: str, depth: int = 1, store=None) -> dict:
    """
    Cypher:
        MATCH (n:Entity {id: $name})-[r*1..$depth]-(m)
        RETURN n, r, m

    Returns a small subgraph {nodes: [...], edges: [...]} for graph-explorer
    style visualization, expanded breadth-first up to `depth` hops.
    """
    store = store or graph_store
    visited_nodes: dict[str, dict] = {}
    edges: list[dict] = []

    frontier = [entity_name]
    seen_edges = set()
    for _ in range(depth):
        next_frontier = []
        for node_id in frontier:
            node = store.get_node(node_id)
            if node and node_id not in visited_nodes:
                visited_nodes[node_id] = node
            for neighbor in store.get_neighbors(node_id, direction="both"):
                target_id = neighbor["node"].get("id")
                edge_key = (node_id, neighbor["relation"], target_id)
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    edges.append({"source": node_id, "relation": neighbor["relation"], "target": target_id})
                if target_id and target_id not in visited_nodes:
                    visited_nodes[target_id] = neighbor["node"]
                    next_frontier.append(target_id)
        frontier = next_frontier

    return {"nodes": list(visited_nodes.values()), "edges": edges}


def find_alternative_shelters(exclude_shelter: str, min_capacity: int = 1, store=None) -> list[dict]:
    """
    Cypher:
        MATCH (s:Entity {type:'Shelter'})
        WHERE s.id <> $exclude AND s.available_capacity >= $min_capacity
        RETURN s
    """
    store = store or graph_store
    shelters = store.find_nodes(node_type="Shelter")
    return [
        s for s in shelters
        if s.get("id") != exclude_shelter and s.get("available_capacity", 0) >= min_capacity
    ]


def multi_hop_shelter_recommendation(area_name: str, store=None) -> dict:
    """
    Multi-hop traversal implementing the core GraphRAG traversal described in
    the project spec:

        Area -> Affected Population -> Shelters -> Available Capacity
              -> Drinking Water -> Medical Support

    Cypher (conceptual):
        MATCH (area:Entity {id:$area})
        OPTIONAL MATCH (area)-[:HAS_SHELTER]->(s:Entity)
        OPTIONAL MATCH (s)-[:HAS_RESOURCE]->(res:Entity)
        RETURN area, s, collect(res) as resources
    """
    store = store or graph_store
    path = {"hops": []}

    area_node = store.get_node(area_name)
    path["hops"].append({"step": "Area", "data": area_node})

    population = find_affected_population(area_name, store)
    path["hops"].append({"step": "Affected Population", "data": population})

    shelters = find_shelters_near_area(area_name, store)
    if not shelters:
        # District-wide fallback: any shelter in the same district.
        shelters = store.find_nodes(node_type="Shelter")
    path["hops"].append({"step": "Candidate Shelters", "data": [s.get("id", s.get("name")) for s in shelters]})

    enriched = []
    for shelter in shelters:
        shelter_id = shelter.get("id", shelter.get("name"))
        resources = [n["relation"] + ":" + n["node"].get("id", "") for n in store.get_neighbors(shelter_id, relation="HAS_RESOURCE")]
        enriched.append({**shelter, "resource_links": resources})

    path["hops"].append({"step": "Shelter Resource Check (Drinking Water / Medical Support)", "data": [e["resource_links"] for e in enriched]})

    return {"area": area_name, "population_affected": population, "shelters": enriched, "reasoning_path": path}
