"""
Disaster response PDF report generator (ReportLab).

Produces a downloadable report covering the situation, shelter
recommendations, resource availability/shortages, hospital availability,
responsible agencies, recommended actions, GraphRAG evidence, source
documents, reasoning path, and the mandatory disclaimer.
"""
from __future__ import annotations

import time
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
)

from app.config import BASE_DIR
from app.disaster.recommendation_engine import generate_recommendation
from app.rag.graphrag_engine import answer_query

REPORTS_DIR = BASE_DIR / "data" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

DISCLAIMER = (
    "This system provides AI-assisted decision support and does not replace "
    "official disaster-management authorities or emergency command decisions."
)


def generate_report(area_name: str) -> str:
    """Builds a PDF report for the given area and returns the file path."""
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleCustom", parent=styles["Title"], textColor=colors.HexColor("#1b3a5c"))
    heading_style = ParagraphStyle("HeadingCustom", parent=styles["Heading2"], textColor=colors.HexColor("#1b3a5c"), spaceBefore=14)
    normal = styles["Normal"]
    small = ParagraphStyle("Small", parent=styles["Normal"], fontSize=8, textColor=colors.grey)

    rec = generate_recommendation(area_name)
    grag = answer_query(f"What response actions are recommended for {area_name}?")

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    filename = f"disaster_report_{area_name.replace(' ', '_')}_{int(time.time())}.pdf"
    out_path = REPORTS_DIR / filename

    doc = SimpleDocTemplate(str(out_path), pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    story = []

    story.append(Paragraph("Disaster Response Report", title_style))
    story.append(Paragraph("DisasterGraph AI — GraphRAG Decision Support (Synthetic Demo Data)", normal))
    story.append(Paragraph(f"Generated: {timestamp}", small))
    story.append(Spacer(1, 16))

    story.append(Paragraph("Disaster Situation", heading_style))
    sit = rec["situation"]
    story.append(Paragraph(f"Disaster type: {sit['disaster_type']}", normal))
    story.append(Paragraph(f"Affected area: {sit['area']}", normal))
    story.append(Paragraph(f"Affected population: {sit['affected_population']}", normal))
    story.append(Paragraph(
        f"Priority level: {rec['priority']['priority_level']} (score {rec['priority']['priority_score']}/100 — demo heuristic)",
        normal,
    ))

    story.append(Paragraph("Shelter Recommendation", heading_style))
    if rec["recommended_shelter"]:
        rs = rec["recommended_shelter"]
        story.append(Paragraph(
            f"Recommended shelter: {rs['id']} — suitability {rs['suitability_percent']}%, available capacity {rs['available_capacity']}",
            normal,
        ))
    else:
        story.append(Paragraph("No shelter data available.", normal))
    if rec["alternative_shelters"]:
        data = [["Alternative Shelter", "Suitability %"]] + [
            [s["id"], str(s["suitability_percent"])] for s in rec["alternative_shelters"]
        ]
        t = Table(data, hAlign="LEFT")
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1b3a5c")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
        ]))
        story.append(Spacer(1, 6))
        story.append(t)

    story.append(Paragraph("Resource Availability &amp; Shortages", heading_style))
    if rec["resource_shortages"]:
        data = [["Resource", "Available", "Required", "Shortage", "Agency"]]
        for r in rec["resource_shortages"]:
            data.append([r["resource"], f"{r['available']} {r['unit']}", f"{r['required']} {r['unit']}", f"{r['shortage']} {r['unit']}", ", ".join(r["responsible_agencies"])])
        t = Table(data, hAlign="LEFT")
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1b3a5c")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
        ]))
        story.append(t)
    else:
        story.append(Paragraph("No significant resource shortages detected.", normal))

    story.append(Paragraph("Hospital Availability", heading_style))
    if rec["hospitals"]:
        for h in rec["hospitals"]:
            story.append(Paragraph(f"{h['id']}: {h['available_emergency_beds']} available emergency beds", normal))
    else:
        story.append(Paragraph("No hospital data available for this area.", normal))

    story.append(Paragraph("Responsible Agencies", heading_style))
    story.append(Paragraph(", ".join(rec["responsible_agencies"]) or "None identified.", normal))

    story.append(Paragraph("Recommended Actions", heading_style))
    for i, action in enumerate(rec["recommended_actions"], start=1):
        story.append(Paragraph(f"{i}. {action}", normal))

    story.append(Paragraph("GraphRAG Evidence &amp; Reasoning Path", heading_style))
    for step in grag.reasoning_path:
        story.append(Paragraph(f"• {step}", normal))

    story.append(Paragraph("Source Documents", heading_style))
    if grag.sources:
        for s in grag.sources:
            story.append(Paragraph(f"• {s['document']} — {s['section']} (relevance {s['relevance_score']})", normal))
    else:
        story.append(Paragraph("No document sources retrieved for this query.", normal))

    story.append(PageBreak())
    story.append(Paragraph("Disclaimer", heading_style))
    story.append(Paragraph(DISCLAIMER, normal))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "All data in this report is synthetic demo data generated for an academic "
        "final-year project and does not represent a real disaster event.",
        small,
    ))

    doc.build(story)
    return str(out_path)
