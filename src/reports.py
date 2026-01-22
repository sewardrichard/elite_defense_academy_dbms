import os
from datetime import date
from src.database import execute_query
# try import reportlab, if fails handle gracefully or assume installed
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, LongTable, KeepTogether, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.graphics.shapes import Drawing, String
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False
    print("Warning: reportlab not installed. PDF reporting will not work.")
    # reportlab is not available; do not import its components here.
    # The PDF functions will check `HAS_REPORTLAB` before use.



def _watermark_canvas(c, doc):
    """Draw an official watermark and signature line on the canvas."""
    width, height = doc.pagesize
    c.saveState()
    c.setFont("Helvetica-Bold", 60)
    c.setFillColorRGB(0.85, 0.85, 0.85)
    c.translate(width / 2.0, height / 2.0)
    c.rotate(45)
    c.drawCentredString(0, 0, "OFFICIAL SEAL")
    c.restoreState()

    # Signature block bottom right
    sig_x = width - 3.5 * inch
    sig_y = 1.25 * inch
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(1)
    c.line(sig_x, sig_y, sig_x + 2.5 * inch, sig_y)
    c.setFont("Helvetica", 10)
    c.drawString(sig_x, sig_y - 12, "Commanding Officer")


def generate_official_transcript(student_id, filename=None):
    """Generate an official transcript PDF for a given student_id.

    Uses the vw_transcript view to pull course rows and computes a simple
    cumulative GPA and total credits. The function requires ReportLab.
    """
    if not HAS_REPORTLAB:
        print("Error: ReportLab library is required for PDF generation.")
        return

    # Fetch transcript rows
    q = "SELECT student_id, service_number, first_name, last_name, course_code, course_name, credits, final_score, grade_letter, start_date, completion_date FROM vw_transcript WHERE student_id = %s ORDER BY start_date"
    rows = execute_query(q, (student_id,), fetch=True)
    if not rows:
        print("No transcript records found for the selected student.")
        return

    # Student metadata (first row)
    meta = rows[0]
    # Cumulative GPA (weighted by credits)
    gpa_q = "SELECT SUM((COALESCE(final_score,0)/25.0) * credits) as weighted_sum, SUM(credits) as total_credits FROM vw_transcript WHERE student_id = %s"
    gpa_res = execute_query(gpa_q, (student_id,), fetch=True)
    weighted_sum = gpa_res[0].get('weighted_sum') if gpa_res and gpa_res[0] else None
    total_credits = gpa_res[0].get('total_credits') if gpa_res and gpa_res[0] else 0
    cumulative_gpa = None
    try:
        if weighted_sum is not None and total_credits:
            cumulative_gpa = round(float(weighted_sum) / float(total_credits), 2)
    except Exception:
        cumulative_gpa = None

    # Prepare PDF
    if not filename:
        # Build filename: {student id}_{name}_{surname}_Official_Transcript.pdf
        fname = f"{meta.get('student_id')}_{str(meta.get('first_name','')).strip().replace(' ','_')}_{str(meta.get('last_name','')).strip().replace(' ','_')}_Official_Transcript.pdf"
        filename = os.path.join("reports", fname)
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Header: academy title (three lines: one word per line) and student meta (one detail per line).
    # Use a slightly smaller title so words don't get squashed; make left column wider.
    academy_style = ParagraphStyle('AcademyTitle', parent=styles['Title'], fontSize=16, leading=18, alignment=1)
    # One word per line
    academy_para = Paragraph("<b>ELITE<br/>DEFENSE<br/>ACADEMY</b>", academy_style)

    today_str = date.today().strftime('%Y-%m-%d')
    # Student meta: bold label then value, one item per line
    student_meta_html = (
        f"<b>Service Number:</b> {meta.get('service_number','')}<br/>"
        f"<b>Name:</b> {meta.get('first_name','')} {meta.get('last_name','')}<br/>"
        f"<b>Student ID:</b> {meta.get('student_id','')}<br/>"
        f"<b>Date:</b> {today_str}<br/>"
    )
    student_style = ParagraphStyle('StudentMeta', parent=styles['Normal'], fontSize=10, leading=14, alignment=0)
    header_data = [[academy_para, Paragraph(student_meta_html, student_style)]]
    # Increase left column width so the three words don't wrap or get cut
    htable = Table(header_data, colWidths=[2.5 * inch, 4.0 * inch])
    htable.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    elements.append(htable)
    elements.append(Spacer(1, 12))

    # Transcript heading with month/year (e.g. OFFICAL TRANSCRIPT - 01/2026)
    heading_style = ParagraphStyle('TranscriptHeading', parent=styles.get('Heading2', styles['Title']), fontSize=12, leading=14, alignment=1)
    heading_text = f"OFFICAL TRANSCRIPT - {date.today().strftime('%m/%Y')}"
    elements.append(Paragraph(heading_text, heading_style))
    elements.append(Spacer(1, 6))

    # Transcript table (LongTable) header
    data = [["Course Code", "Course Name", "Credits", "Grade"]]
    for r in rows:
        data.append([r.get('course_code',''), r.get('course_name',''), str(r.get('credits','')), r.get('grade_letter','') or "-"])

    lt = LongTable(data, repeatRows=1, colWidths=[1.2*inch, 3.6*inch, 0.8*inch, 0.8*inch])
    lt_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#333333')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (2, 1), (3, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ])

    # Zebra striping
    for i in range(1, len(data)):
        bg = colors.whitesmoke if i % 2 == 1 else colors.white
        lt_style.add('BACKGROUND', (0, i), (-1, i), bg)

    lt.setStyle(lt_style)
    elements.append(lt)
    elements.append(Spacer(1, 12))

    # Summary block (KeepTogether)
    summary_lines = []
    summary_lines.append(Paragraph(f"<b>Total Credits:</b> {total_credits}", styles['Normal']))
    summary_lines.append(Paragraph(f"<b>Cumulative GPA:</b> {cumulative_gpa if cumulative_gpa is not None else 'N/A'}", styles['Normal']))
    elements.append(KeepTogether(summary_lines))
    elements.append(Spacer(1, 48))

    # Signature line placeholder
    elements.append(Paragraph("", styles['Normal']))

    try:
        doc.build(elements, onFirstPage=_watermark_canvas, onLaterPages=_watermark_canvas)
        print(f"Official transcript saved to {filename}")
    except Exception as e:
        print(f"Error generating transcript PDF: {e}")
def generate_company_readiness_ledger(filename=None, support_threshold_pct=60):
    """Generate a Company Readiness & Performance Ledger PDF.

    - Bar chart: average GPA per company (visual quality focused)
    - Summary table: commanding_officer and % students in Good Standing
    - Key insight: companies below thresholds are flagged for support
    """
    if not HAS_REPORTLAB:
        print("Error: ReportLab library is required for PDF generation.")
        return

    # Aggregate by company using pre-computed performance_summary where possible
    q = """
    SELECT co.company_name, co.commanding_officer,
           AVG(ps.gpa) AS avg_gpa,
           SUM(CASE WHEN ps.current_standing ILIKE 'Good%' THEN 1 ELSE 0 END) AS good_count,
           COUNT(*) AS total_students
    FROM companies co
    JOIN students s ON s.company_id = co.company_id
    JOIN performance_summary ps ON ps.student_id = s.student_id
    GROUP BY co.company_name, co.commanding_officer
    ORDER BY avg_gpa DESC
    """

    rows = execute_query(q, fetch=True)
    if not rows:
        print("No company performance data available.")
        return

    # Build output filename
    if not filename:
        fname = f"Company_Readiness_Ledger_{date.today().strftime('%Y%m%d')}.pdf"
        filename = os.path.join("reports", fname)
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # Prepare PDF document
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle('TitleSmall', parent=styles['Title'], fontSize=16, alignment=1)
    elements.append(Paragraph("Company Readiness & Performance Ledger", title_style))
    elements.append(Spacer(1, 12))

    # Prepare bar chart data (avg GPA per company)
    company_names = [r.get('company_name') or 'Unknown' for r in rows]
    # Ensure numeric values are plain floats (DB may return Decimal)
    avg_gpas = [float(r.get('avg_gpa') or 0.0) for r in rows]

    # Chart drawing
    chart_width = 420
    chart_height = 220
    drawing = Drawing(chart_width, chart_height)

    bc = VerticalBarChart()
    bc.x = 50
    bc.y = 30
    bc.width = chart_width - 100
    bc.height = chart_height - 60
    bc.data = [avg_gpas]
    bc.strokeColor = colors.black
    bc.valueAxis.valueMin = 0
    # Expect GPA on 4.0 scale; set upper bound slightly above max for breathing room
    try:
        max_val = max(avg_gpas) if avg_gpas else 4.0
        bc.valueAxis.valueMax = max(4.0, float(max_val) + 0.5)
    except Exception:
        bc.valueAxis.valueMax = 4.0

    bc.valueAxis.valueStep = 0.5
    # Color bars with a pleasant palette
    bc.bars.strokeWidth = 0.5
    bc.bars.fillColor = colors.HexColor('#2E86AB')
    bc.categoryAxis.categoryNames = company_names
    bc.categoryAxis.labels.angle = 45
    drawing.add(bc)
    drawing.add(String(10, chart_height - 10, "Average GPA by Company", fontSize=10))

    elements.append(drawing)
    elements.append(Spacer(1, 18))

    # Summary table: company, commanding_officer, avg_gpa, % good standing, students
    table_data = [["Company", "Commanding Officer", "Avg GPA", "% Good Standing", "Students"]]
    insights = []
    for i, r in enumerate(rows):
        total = int(r.get('total_students') or 0)
        good = int(r.get('good_count') or 0)
        pct = round((good / total * 100), 1) if total else 0.0
        avg_val = float(r.get('avg_gpa') or 0.0)
        table_data.append([
            r.get('company_name') or '',
            r.get('commanding_officer') or '',
            f"{avg_val:.2f}",
            f"{pct}%",
            str(total)
        ])

        # Flag for insight
        if pct < support_threshold_pct or avg_val < 2.5:
            insights.append(f"{r.get('company_name')}: requires instructional support (Avg GPA {avg_val:.2f}, {pct}% good)")

    tbl = Table(table_data, colWidths=[2.25*inch, 1.75*inch, 0.8*inch, 1.0*inch, 0.7*inch])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#333333')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(tbl)
    elements.append(Spacer(1, 12))

    # Insights block
    insight_style = ParagraphStyle('Insight', parent=styles['Normal'], fontSize=10, leading=12)
    elements.append(Paragraph("<b>Key Insights</b>", styles['Heading3']))
    if insights:
        for ins in insights:
            elements.append(Paragraph(f"- {ins}", insight_style))
    else:
        elements.append(Paragraph("All companies meeting readiness thresholds.", insight_style))

    try:
        doc.build(elements, onFirstPage=_watermark_canvas, onLaterPages=_watermark_canvas)
        print(f"Company Readiness Ledger saved to {filename}")
    except Exception as e:
        print(f"Error generating company readiness PDF: {e}")
