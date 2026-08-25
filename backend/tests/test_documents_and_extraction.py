from __future__ import annotations

from app.config import DOCUMENTS_DIR
from app.documents.chunker import chunk_document
from app.documents.parser import parse_document
from app.graph.entity_extractor import extract_entities
from app.graph.relation_extractor import extract_relations


def test_parse_pdf():
    parsed = parse_document(DOCUMENTS_DIR / "flood_response_guidelines.pdf")
    assert parsed.file_type == "pdf"
    assert "Flood" in parsed.full_text
    assert len(parsed.sections) > 0


def test_parse_docx():
    parsed = parse_document(DOCUMENTS_DIR / "disaster_agency_roles.docx")
    assert parsed.file_type == "docx"
    assert "Fire and Rescue" in parsed.full_text


def test_parse_txt():
    parsed = parse_document(DOCUMENTS_DIR / "hospital_emergency_guidelines.txt")
    assert "Hospital" in parsed.full_text


def test_chunking_produces_chunks():
    parsed = parse_document(DOCUMENTS_DIR / "emergency_shelter_guidelines.txt")
    chunks = chunk_document(parsed)
    assert len(chunks) > 0
    assert all(c.text for c in chunks)


def test_entity_extraction_finds_known_entities():
    entities = extract_entities("Shelter B is located in Area B and has drinking water.")
    canonicals = {e.canonical for e in entities}
    assert "Shelter B - Community Hall" in canonicals
    assert "Area B" in canonicals


def test_relation_extraction_location():
    relations = extract_relations("Shelter A is located in Area A and can accommodate 600 people.")
    predicates = {r.predicate for r in relations}
    assert "LOCATED_IN" in predicates
    assert "HAS_CAPACITY" in predicates


def test_relation_extraction_responsibility():
    relations = extract_relations("The Fire and Rescue Department is responsible for Rescue Operation.")
    assert any(r.predicate == "RESPONSIBLE_FOR" for r in relations)
