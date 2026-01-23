import os
import csv
from datetime import date
from src.database import execute_query
# try import core reportlab components first; charts are optional
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, LongTable, KeepTogether, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.graphics.shapes import Drawing, String
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    HAS_REPORTLAB = True
except Exception:
    HAS_REPORTLAB = False
    print("Warning: reportlab not installed. PDF reporting will not work.")
    # reportlab is not available; do not import its components here.
    # The PDF functions will check `HAS_REPORTLAB` before use.
# Optional graphics/chart imports (pie charts)
try:
    from reportlab.graphics.charts.pie import Pie
    from reportlab.graphics import renderPDF
    HAS_PIE = True
except Exception:
    HAS_PIE = False


def export_to_csv(query, filename):
    """Execute a query and write results to a CSV file."""
    results = execute_query(query, fetch=True)
    if not results:
        print("No data found to export.")
        return

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # results are expected to be list of dict-like objects
            headers = list(results[0].keys())
            writer.writerow(headers)
            for row in results:
                writer.writerow([row.get(h, '') for h in headers])
        print(f"CSV exported to {filename}")
    except Exception as e:
        print(f"Error exporting CSV: {e}")


def export_to_pdf(query, title, filename):
    """Execute a query and write a simple table PDF using ReportLab."""
    if not HAS_REPORTLAB:
        print("Error: ReportLab library is required for PDF generation.")
        return

    results = execute_query(query, fetch=True)
    if not results:
        print("No data found to export.")
        return

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    try:
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = [Paragraph(title, styles['Title']), Spacer(1, 12)]

        headers = list(results[0].keys())
        data = [headers]
        for row in results:
            data.append([str(row.get(h, '')) for h in headers])

        t = Table(data, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        elements.append(t)
        doc.build(elements)
        print(f"PDF exported to {filename}")
    except Exception as e:
        print(f"Error exporting PDF: {e}")


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
def generate_attendance_report(format='csv'):
    """Generate Attendance Report."""
    query = "SELECT * FROM vw_attendance_report LIMIT 100" # Limit for PDF safety
    filename = os.path.join("reports", f"attendance_report.{format}")
    if format == 'csv':
        export_to_csv(query, filename)
    elif format == 'pdf':
        export_to_pdf(query, "Attendance Report", filename)


def generate_attrition_watchlist_report(format='csv'):
    """Generate Attrition Risk & Intervention Watchlist report.

    Data sources: attrition_risk and vw_low_attendance.
    For CSV the raw query is exported. For PDF, applies conditional
    formatting (Critical -> red, High -> orange) and wraps
    `contributing_factors` using a Paragraph flowable.
    """
    query = """
    SELECT ar.student_id,
           s.service_number,
           s.first_name,
           s.last_name,
           ar.risk_score,
           ar.risk_level,
           ar.contributing_factors,
           va.course_id AS low_att_course_id,
           va.course_code,
           va.course_name AS low_att_course_name,
           va.attendance_rate
    FROM attrition_risk ar
    JOIN students s ON s.student_id = ar.student_id
    LEFT JOIN vw_low_attendance va ON va.student_id = ar.student_id
    ORDER BY 
      CASE WHEN ar.risk_level = 'Critical' THEN 1
           WHEN ar.risk_level = 'High' THEN 2
           WHEN ar.risk_level = 'Medium' THEN 3
           ELSE 4 END,
      ar.risk_score DESC
    """

    filename = os.path.join("reports", f"attrition_watchlist.{format}")

    if format == 'csv':
        export_to_csv(query, filename)
        return

    # PDF path
    if not HAS_REPORTLAB:
        print("Error: ReportLab library is required for PDF generation.")
        return

    results = execute_query(query, fetch=True)
    if not results:
        print("No data found to export.")
        return

    try:
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph("Attrition Risk & Intervention Watchlist", styles['Title']))

        # Prepare table header and rows, using Paragraph for contributing_factors
        headers = list(results[0].keys())
        data = [headers]

        # Build rows with Paragraph for long text column
        for row in results:
            r = []
            for h in headers:
                val = row.get(h)
                if h == 'contributing_factors':
                    # wrap long text in a Paragraph so it flows inside table cell
                    p = Paragraph(str(val or ''), styles['BodyText'])
                    r.append(p)
                else:
                    r.append(str(val) if val is not None else '')
            data.append(r)

        t = Table(data, repeatRows=1)

        # Base table style
        tbl_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]

        # Add conditional row-level formatting for risk levels
        # Find column index for risk_level
        try:
            risk_col = headers.index('risk_level')
        except ValueError:
            risk_col = None

        for idx, row in enumerate(results, start=1):
            rl = (row.get('risk_level') or '').lower()
            if rl == 'critical':
                # color the risk level cell red
                if risk_col is not None:
                    tbl_style.append(('BACKGROUND', (risk_col, idx), (risk_col, idx), colors.red))
                    tbl_style.append(('TEXTCOLOR', (risk_col, idx), (risk_col, idx), colors.whitesmoke))
            elif rl == 'high':
                if risk_col is not None:
                    tbl_style.append(('BACKGROUND', (risk_col, idx), (risk_col, idx), colors.orange))

        t.setStyle(TableStyle(tbl_style))
        elements.append(t)

        doc.build(elements)
        print(f"PDF Report saved to {filename}")
    except Exception as e:
        print(f"Error saving PDF: {e}")


def generate_course_grit_report(format='csv'):
    """Generate Course Grit & Grade Distribution Analysis.

    Data Source: vw_course_avg_grades and vw_course_enrollment_stats.
    Produces CSV with aggregated A/B/C/D-F buckets per department and
    a PDF with a pie chart per department plus a small statistics table
    showing total_enrollments vs failed_count.
    """
    # Aggregate by department token from course_code (prefix before '-')
    agg_query = """
    WITH grit AS (
      SELECT split_part(course_code, '-', 1) AS department,
             SUM(a_bucket) AS a_bucket,
             SUM(b_bucket) AS b_bucket,
             SUM(c_bucket) AS c_bucket,
             SUM(d_f_bucket) AS d_f_bucket,
             SUM(enrollments) AS enrollments
      FROM vw_course_avg_grades
      GROUP BY department
    ), failures AS (
      SELECT split_part(course_code, '-', 1) AS department,
             SUM(total_enrollments) AS total_enrollments,
             SUM(failed_count) AS failed_count
      FROM vw_course_enrollment_stats
      GROUP BY department
    )
    SELECT g.department, g.a_bucket, g.b_bucket, g.c_bucket, g.d_f_bucket, g.enrollments,
           COALESCE(f.total_enrollments, 0) AS total_enrollments, COALESCE(f.failed_count, 0) AS failed_count
    FROM grit g
    LEFT JOIN failures f ON f.department = g.department
    ORDER BY g.department
    """

    filename = os.path.join("reports", f"course_grit.{format}")

    if format == 'csv':
        export_to_csv(agg_query, filename)
        return

    if not HAS_REPORTLAB:
        print("Error: ReportLab library is required for PDF generation.")
        return

    rows = execute_query(agg_query, fetch=True)
    if not rows:
        print("No data found to export.")
        return

    try:
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph("Course Grit & Grade Distribution Analysis", styles['Title']))

        # For each department create a small pie chart and a stats table
        for r in rows:
            dept = r.get('department')
            a = int(r.get('a_bucket') or 0)
            b = int(r.get('b_bucket') or 0)
            c = int(r.get('c_bucket') or 0)
            d = int(r.get('d_f_bucket') or 0)
            total_enroll = int(r.get('enrollments') or 0)
            failed = int(r.get('failed_count') or 0)

            elements.append(Paragraph(f"Department: {dept}", styles['Heading2']))

            # Pie chart (optional). If pie charts are unavailable, show a buckets table instead.
            if 'HAS_PIE' in globals() and HAS_PIE:
                drawing = Drawing(200, 140)
                pc = Pie()
                pc.x = 65
                pc.y = 15
                pc.width = 70
                pc.height = 70
                pc.data = [a, b, c, d]
                pc.labels = [f"A ({a})", f"B ({b})", f"C ({c})", f"D/F ({d})"]
                try:
                    pc.slices.strokeWidth = 0.5
                    # assign basic colors if slices exist
                    if len(pc.slices) >= 4:
                        pc.slices[0].fillColor = colors.green
                        pc.slices[1].fillColor = colors.blue
                        pc.slices[2].fillColor = colors.yellow
                        pc.slices[3].fillColor = colors.red
                except Exception:
                    pass

                drawing.add(pc)
                # Add legend text
                try:
                    drawing.add(String(140, 110, f"Total Enroll: {total_enroll}", fontSize=8))
                    drawing.add(String(140, 98, f"Failed: {failed}", fontSize=8))
                except Exception:
                    pass

                elements.append(drawing)
            else:
                # Fallback: show bucket counts as a small table when pie chart isn't available
                bucket_data = [["Bucket", "Count"], ["A", str(a)], ["B", str(b)], ["C", str(c)], ["D/F", str(d)]]
                bt = Table(bucket_data, hAlign='LEFT')
                bt.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ]))
                elements.append(bt)

            # Stats table
            stats_data = [["Metric", "Value"], ["Total Enrollments", str(total_enroll)], ["Failed Count", str(failed)]]
            st = Table(stats_data, hAlign='LEFT')
            st.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ]))
            elements.append(st)

            # small spacer
            elements.append(Paragraph(" ", styles['Normal']))

        doc.build(elements)
        print(f"PDF Report saved to {filename}")
    except Exception as e:
        print(f"Error saving PDF: {e}")


def generate_daily_muster_report(format='csv'):
    """Generate Daily Muster (Attendance) Accountability Report.

    Data Source: vw_attendance_report for daily roll-ups and `attendance`
    for exceptions (AWOL / Absent) including `recorded_by` and `remarks`.
    """
    rollup_query = """
    SELECT muster_date, course_id, course_code, course_name,
           present_count, late_count, awol_count, absent_count, excused_count, total_records
    FROM vw_attendance_report
    ORDER BY muster_date DESC
    """

    exceptions_query = """
    SELECT a.muster_date, a.student_id, s.service_number, s.first_name, s.last_name,
           c.course_code, a.status, a.recorded_by, a.remarks
    FROM attendance a
    JOIN students s ON s.student_id = a.student_id
    JOIN courses c ON c.course_id = a.course_id
    WHERE a.status IN ('AWOL', 'Absent')
    ORDER BY a.muster_date DESC
    """

    filename = os.path.join("reports", f"daily_muster.{format}")

    # CSV: write rollup and exceptions as two separate files for clarity
    if format == 'csv':
        export_to_csv(rollup_query, filename)
        export_to_csv(exceptions_query, os.path.join("reports", "daily_muster_exceptions.csv"))
        return

    if not HAS_REPORTLAB:
        print("Error: ReportLab library is required for PDF generation.")
        return

    rollups = execute_query(rollup_query, fetch=True)
    exceptions = execute_query(exceptions_query, fetch=True)

    if not rollups and not exceptions:
        print("No data found to export.")
        return

    try:
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph("Daily Muster (Attendance) Accountability Report", styles['Title']))

        if rollups:
            elements.append(Paragraph("Daily Roll-up (by muster_date)", styles['Heading2']))
            headers = list(rollups[0].keys())
            data = [headers]
            for row in rollups:
                data.append([str(row.get(h, '')) for h in headers])

            t = Table(data, repeatRows=1)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ]))
            elements.append(t)

        if exceptions:
            elements.append(Paragraph("Exceptions (AWOL / Absent)", styles['Heading2']))
            ex_headers = list(exceptions[0].keys())
            ex_data = [ex_headers]
            for row in exceptions:
                # Wrap remarks in Paragraph so long text flows
                row_vals = []
                for h in ex_headers:
                    if h == 'remarks':
                        row_vals.append(Paragraph(str(row.get(h) or ''), styles['BodyText']))
                    else:
                        row_vals.append(str(row.get(h, '')))
                ex_data.append(row_vals)

            et = Table(ex_data, repeatRows=1)
            et.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ]))
            elements.append(et)

        doc.build(elements)
        print(f"PDF Report saved to {filename}")
    except Exception as e:
        print(f"Error saving PDF: {e}")
