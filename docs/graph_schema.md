# Knowledge Graph Schema

## Node Types

| Type | Example | Key Properties |
|---|---|---|
| `Disaster` | Flood | type, date, severity, district, description |
| `Location` | Area A, Salem District | affected_population, district |
| `Shelter` | Shelter B - Community Hall | capacity, occupied, available_capacity, drinking_water, food_available, medical_support, contact, facilities |
| `Resource` | Drinking Water | unit, available, required, shortage |
| `Agency` | Fire and Rescue Department | operates_in |
| `Hospital` | Salem General Hospital (Demo) | total_beds, emergency_beds, available_emergency_beds, facilities |
| `Incident` | Incident INC-001 | date, disaster_type, severity, population_affected, notes |
| `ResponseAction` | Evacuation | — |
| `Entity` | (document-derived mentions not otherwise typed) | source_document |

## Relationship Types

| Relationship | From → To | Meaning |
|---|---|---|
| `AFFECTED` | Disaster → Location | The disaster affected this location |
| `OCCURRED_IN` | Incident → Location | An incident occurred at this location |
| `CAUSED` | Disaster → Incident | The disaster caused this incident |
| `HAS_SHELTER` | Location → Shelter | This location hosts this shelter |
| `LOCATED_IN` | Shelter/Hospital → Location | This facility is located in this area |
| `HAS_RESOURCE` | Shelter → Resource | This shelter currently has this resource available |
| `REQUIRES` | Disaster → Resource | This disaster-type requires this resource |
| `SUPPLIES` | Agency → Resource | This agency is responsible for supplying this resource |
| `RESPONSIBLE_FOR` | Agency → ResponseAction | This agency is responsible for this response action |
| `OPERATES_IN` | Agency → Location | This agency operates in this location |
| `REQUIRES_ACTION` | Disaster → ResponseAction | This disaster-type requires this response action |
| `HAS_HOSPITAL` | Location → Hospital | This location has this hospital |
| (document-derived, dynamic) | Entity → Entity | Extracted by `relation_extractor.py` from free text, e.g. `LOCATED_IN`, `HAS_CAPACITY`, `RESPONSIBLE_FOR`, `AFFECTED` |

## Node ID Strategy

Node IDs are the **canonical entity name** (see `entity_normalizer.py`), not
an arbitrary UUID. This means structured demo data (e.g. "Salem District")
and document-derived mentions (e.g. "Salem", "salem district") resolve to
the *same* graph node instead of creating duplicates, because both are
mapped through the same alias table before being written to the graph.

## Example Subgraph (Flood)

```text
Flood
 ├── AFFECTED → Area A
 │                ├── HAS_SHELTER → Shelter A - Government High School
 │                │                    └── HAS_RESOURCE → Food Packets
 │                └── HAS_SHELTER → Shelter D - Town Community Center
 ├── AFFECTED → Area B
 │                └── HAS_SHELTER → Shelter B - Community Hall
 │                                     ├── HAS_RESOURCE → Drinking Water
 │                                     └── HAS_RESOURCE → Medical Support
 ├── REQUIRES → Drinking Water
 ├── REQUIRES → Rescue Boats
 └── REQUIRES_ACTION → Evacuation
                          └── (RESPONSIBLE_FOR) ← Fire and Rescue Department
```

## Storage Backend

- **Preferred**: Neo4j (`app/graph/graph_store.py:Neo4jGraphStore`), using
  a single generic `:Entity` label with a `type` property (rather than one
  Neo4j label per type) so that Cypher queries stay simple and uniform
  across all entity types. Relationship types map directly to Neo4j
  relationship types (sanitized to alphanumeric + underscore).
- **Fallback**: an in-memory `networkx.MultiDiGraph`
  (`InMemoryGraphStore`), exposing the identical interface so the rest of
  the application is backend-agnostic.
