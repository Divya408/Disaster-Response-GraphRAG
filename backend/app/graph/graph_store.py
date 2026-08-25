"""
Graph storage layer.

Preferred backend: Neo4j (via the official `neo4j` Python driver), configured
through NEO4J_URI / NEO4J_USERNAME / NEO4J_PASSWORD.

Fallback backend: an in-memory networkx MultiDiGraph, automatically used when
Neo4j is not configured, not installed, or not reachable — so the project
always remains demonstrable even without a running Neo4j instance.

Both backends expose the same small interface (`add_node`, `add_edge`,
`get_neighbors`, `find_nodes`, `get_node`, `all_nodes`, `all_edges`,
`clear`), so the rest of the application never needs to know which backend
is active.
"""
from __future__ import annotations

import threading
from typing import Any, Iterable

import networkx as nx

from app.config import settings


class InMemoryGraphStore:
    """networkx-backed fallback graph store."""

    def __init__(self):
        self._graph = nx.MultiDiGraph()
        self._lock = threading.Lock()

    def clear(self):
        with self._lock:
            self._graph = nx.MultiDiGraph()

    def add_node(self, node_id: str, node_type: str, **properties):
        properties.pop("type", None)  # node_type is authoritative; avoid kwarg clashes
        with self._lock:
            if self._graph.has_node(node_id):
                self._graph.nodes[node_id].update(properties)
                self._graph.nodes[node_id]["type"] = node_type
            else:
                self._graph.add_node(node_id, type=node_type, **properties)

    def add_edge(self, source_id: str, relation: str, target_id: str, **properties):
        with self._lock:
            if not self._graph.has_node(source_id):
                self._graph.add_node(source_id, type="Unknown")
            if not self._graph.has_node(target_id):
                self._graph.add_node(target_id, type="Unknown")
            self._graph.add_edge(source_id, target_id, key=relation, relation=relation, **properties)

    def get_node(self, node_id: str) -> dict | None:
        if self._graph.has_node(node_id):
            data = dict(self._graph.nodes[node_id])
            data["id"] = node_id
            return data
        return None

    def find_nodes(self, node_type: str | None = None, name_contains: str | None = None) -> list[dict]:
        out = []
        for node_id, data in self._graph.nodes(data=True):
            if node_type and data.get("type") != node_type:
                continue
            if name_contains and name_contains.lower() not in str(data.get("name", node_id)).lower():
                continue
            row = dict(data)
            row["id"] = node_id
            out.append(row)
        return out

    def get_neighbors(self, node_id: str, relation: str | None = None, direction: str = "out") -> list[dict]:
        results = []
        if direction in ("out", "both") and self._graph.has_node(node_id):
            for _, target, key, data in self._graph.out_edges(node_id, keys=True, data=True):
                if relation and key != relation:
                    continue
                node_data = self.get_node(target) or {"id": target}
                results.append({"relation": key, "node": node_data, "edge_properties": data})
        if direction in ("in", "both") and self._graph.has_node(node_id):
            for source, _, key, data in self._graph.in_edges(node_id, keys=True, data=True):
                if relation and key != relation:
                    continue
                node_data = self.get_node(source) or {"id": source}
                results.append({"relation": key, "node": node_data, "edge_properties": data})
        return results

    def all_nodes(self) -> list[dict]:
        return self.find_nodes()

    def all_edges(self) -> list[dict]:
        edges = []
        for source, target, key, data in self._graph.edges(keys=True, data=True):
            edges.append({"source": source, "target": target, "relation": key, **data})
        return edges

    def node_count(self) -> int:
        return self._graph.number_of_nodes()

    def edge_count(self) -> int:
        return self._graph.number_of_edges()

    @property
    def backend_name(self) -> str:
        return "in-memory (networkx fallback)"


class Neo4jGraphStore:
    """Neo4j-backed graph store. Only instantiated if the driver connects successfully."""

    def __init__(self, uri: str, username: str, password: str):
        from neo4j import GraphDatabase  # imported lazily; optional dependency

        self._driver = GraphDatabase.driver(uri, auth=(username, password))
        # Verify connectivity eagerly so callers fail fast and can fall back.
        self._driver.verify_connectivity()

    def close(self):
        self._driver.close()

    def clear(self):
        with self._driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def add_node(self, node_id: str, node_type: str, **properties):
        with self._driver.session() as session:
            session.run(
                f"MERGE (n:Entity {{id: $id}}) SET n += $props, n.type = $type",
                id=node_id, type=node_type, props=properties,
            )

    def add_edge(self, source_id: str, relation: str, target_id: str, **properties):
        safe_relation = "".join(c for c in relation if c.isalnum() or c == "_") or "RELATED_TO"
        with self._driver.session() as session:
            session.run(
                f"""
                MERGE (a:Entity {{id: $source_id}})
                MERGE (b:Entity {{id: $target_id}})
                MERGE (a)-[r:{safe_relation}]->(b)
                SET r += $props
                """,
                source_id=source_id, target_id=target_id, props=properties,
            )

    def get_node(self, node_id: str) -> dict | None:
        with self._driver.session() as session:
            result = session.run("MATCH (n:Entity {id: $id}) RETURN n", id=node_id).single()
            if not result:
                return None
            data = dict(result["n"])
            data["id"] = node_id
            return data

    def find_nodes(self, node_type: str | None = None, name_contains: str | None = None) -> list[dict]:
        query = "MATCH (n:Entity) WHERE 1=1"
        params: dict[str, Any] = {}
        if node_type:
            query += " AND n.type = $type"
            params["type"] = node_type
        if name_contains:
            query += " AND toLower(coalesce(n.name, n.id)) CONTAINS toLower($name)"
            params["name"] = name_contains
        query += " RETURN n"
        with self._driver.session() as session:
            rows = session.run(query, **params)
            return [dict(r["n"]) for r in rows]

    def get_neighbors(self, node_id: str, relation: str | None = None, direction: str = "out") -> list[dict]:
        rel_clause = f":{relation}" if relation else ""
        if direction == "out":
            query = f"MATCH (n:Entity {{id: $id}})-[r{rel_clause}]->(m) RETURN type(r) as rel, m, r"
        elif direction == "in":
            query = f"MATCH (n:Entity {{id: $id}})<-[r{rel_clause}]-(m) RETURN type(r) as rel, m, r"
        else:
            query = f"MATCH (n:Entity {{id: $id}})-[r{rel_clause}]-(m) RETURN type(r) as rel, m, r"
        with self._driver.session() as session:
            rows = session.run(query, id=node_id)
            return [{"relation": r["rel"], "node": dict(r["m"]), "edge_properties": dict(r["r"])} for r in rows]

    def all_nodes(self) -> list[dict]:
        return self.find_nodes()

    def all_edges(self) -> list[dict]:
        with self._driver.session() as session:
            rows = session.run("MATCH (a:Entity)-[r]->(b) RETURN a.id as source, b.id as target, type(r) as relation")
            return [dict(r) for r in rows]

    def node_count(self) -> int:
        with self._driver.session() as session:
            return session.run("MATCH (n:Entity) RETURN count(n) as c").single()["c"]

    def edge_count(self) -> int:
        with self._driver.session() as session:
            return session.run("MATCH ()-[r]->() RETURN count(r) as c").single()["c"]

    @property
    def backend_name(self) -> str:
        return "Neo4j"


def build_graph_store():
    """
    Attempt to connect to Neo4j using configured environment variables.
    Falls back to the in-memory store on any failure (missing config, driver
    not installed, connection refused, auth failure, etc.) so the project
    always remains runnable in Demo Mode.
    """
    if settings.NEO4J_URI and settings.NEO4J_USERNAME and settings.NEO4J_PASSWORD:
        try:
            return Neo4jGraphStore(settings.NEO4J_URI, settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
        except Exception:
            pass
    return InMemoryGraphStore()


# Module-level singleton used across the app.
graph_store = build_graph_store()
