#!/usr/bin/env python3
"""Generate a mock official transcript PDF for review.

Creates a sample PDF in the `reports/` folder using ReportLab.
"""
import os
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, LongTable, KeepTogether, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
except ImportError:
    print("ReportLab is required to run this script. Install with: pip install reportlab")
    raise

from datetime import date


def _watermark_canvas(c, doc):
    width, height = doc.pagesize
    c.saveState()
    c.setFont("Helvetica-Bold", 48)
    c.setFillColorRGB(0.92, 0.92, 0.92)
    c.translate(width / 2.0, height / 2.0)
    c.rotate(45)
    c.drawCentredString(0, 0, "OFFICIAL SEAL")
    c.restoreState()


def generate_mock_pdf(outpath=None):
    if not outpath:
        outpath = os.path.join("reports", "mock_official_transcript_John_Doe_123_Official_Transcript.pdf")
    os.makedirs(os.path.dirname(outpath), exist_ok=True)

    doc = SimpleDocTemplate(outpath, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Header: academy title (three lines) and student meta
    academy_style = ParagraphStyle('AcademyTitle', parent=styles['Title'], fontSize=16, leading=18, alignment=1)
    academy_para = Paragraph("<b>ELITE<br/>DEFENSE<br/>ACADEMY</b>", academy_style)

    today_str = date.today().strftime('%Y-%m-%d')
    student_meta_html = (
        f"<b>Service Number:</b> SN-001<br/>"
        f"<b>Name:</b> John Doe<br/>"
        f"<b>Student ID:</b> 123<br/>"
        f"<b>Date:</b> {today_str}<br/>"
    )
    student_style = ParagraphStyle('StudentMeta', parent=styles['Normal'], fontSize=10, leading=14, alignment=0)

    header_data = [[academy_para, Paragraph(student_meta_html, student_style)]]
    htable = Table(header_data, colWidths=[2.5 * inch, 4.0 * inch])
    htable.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    elements.append(htable)
    elements.append(Spacer(1, 12))

    # Heading
    heading_style = ParagraphStyle('TranscriptHeading', parent=styles.get('Heading2', styles['Title']), fontSize=12, leading=14, alignment=1)
    heading_text = "OFFICAL TRANSCRIPT - 01/2026"
    elements.append(Paragraph(heading_text, heading_style))
    elements.append(Spacer(1, 6))

    # Grades table
    data = [["Course Code", "Course Name", "Credits", "Grade"]]
    sample_rows = [
        ("TAC-101", "Basic Tactics", 3, "A"),
        ("WPN-202", "Weapons Handling", 4, "B+"),
        ("ENG-300", "Engineering Basics", 2, "A-"),
    ]
    for r in sample_rows:
        data.append([r[0], r[1], str(r[2]), r[3]])

    tbl = LongTable(data, repeatRows=1, colWidths=[1.2*inch, 3.6*inch, 0.8*inch, 0.8*inch])
    tbl_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#333333')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (2, 1), (3, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ])
    for i in range(1, len(data)):
        bg = colors.whitesmoke if i % 2 == 1 else colors.white
        tbl_style.add('BACKGROUND', (0, i), (-1, i), bg)
    tbl.setStyle(tbl_style)
    elements.append(tbl)
    elements.append(Spacer(1, 12))

    # Summary
    summary_lines = []
    summary_lines.append(Paragraph(f"<b>Total Credits:</b> 9", styles['Normal']))
    summary_lines.append(Paragraph(f"<b>Cumulative GPA:</b> 3.67", styles['Normal']))
    elements.append(KeepTogether(summary_lines))
    elements.append(Spacer(1, 48))

    # Build
    doc.build(elements, onFirstPage=_watermark_canvas, onLaterPages=_watermark_canvas)
    print(f"Mock transcript generated: {outpath}")


if __name__ == '__main__':
    generate_mock_pdf()
