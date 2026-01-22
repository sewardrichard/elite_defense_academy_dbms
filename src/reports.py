import csv
import os
from src.database import execute_query
# try import reportlab, if fails handle gracefully or assume installed
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False
    print("Warning: reportlab not installed. PDF reporting will not work.")

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
