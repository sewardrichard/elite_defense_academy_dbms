import csv
import os
from src.database import execute_query
# try import core reportlab components first; charts are optional
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    HAS_REPORTLAB = True
except Exception:
    HAS_REPORTLAB = False
    print("Warning: reportlab not installed. PDF reporting will not work.")

# Optional graphics/chart imports (pie charts)
try:
    from reportlab.graphics.shapes import Drawing, String
    from reportlab.graphics.charts.pie import Pie
    from reportlab.graphics import renderPDF
    HAS_PIE = True
except Exception:
    HAS_PIE = False

def export_to_csv(query, filename):
    """Execute query and export to CSV."""
    results = execute_query(query, fetch=True)
    if not results:
        print("No data found to export.")
        return

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            # Assumes results is a list of RealDictRow, so keys are available
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        print(f"Report saved to {filename}")
    except Exception as e:
        print(f"Error saving CSV: {e}")

def export_to_pdf(query, title, filename):
    """Execute query and export to PDF."""
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

        # Title
        elements.append(Paragraph(title, styles['Title']))
        
        # Table Data
        if results:
            # Header
            headers = list(results[0].keys())
            data = [headers]
            # Rows
            for row in results:
                data.append([str(row[k]) for k in headers])

            t = Table(data)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(t)

        doc.build(elements)
        print(f"PDF Report saved to {filename}")
    except Exception as e:
        print(f"Error saving PDF: {e}")

def generate_roster_report(format='csv'):
    """Generate Student Roster Report (Course Roster)."""
    query = "SELECT * FROM vw_course_roster"
    
    filename = os.path.join("reports", f"student_roster.{format}")
    if format == 'csv':
        export_to_csv(query, filename)
    elif format == 'pdf':
        export_to_pdf(query, "Student Roster", filename)

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
