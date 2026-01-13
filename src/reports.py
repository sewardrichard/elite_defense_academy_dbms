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
    # Fallback if view doesn't exist, though it should per docs. 
    # Just in case, let's assume it exists or use a raw query if it fails? 
    # The user instructions imply views exist.
    
    filename = f"student_roster.{format}"
    if format == 'csv':
        export_to_csv(query, filename)
    elif format == 'pdf':
        export_to_pdf(query, "Student Roster", filename)

def generate_attendance_report(format='csv'):
    """Generate Attendance Report."""
    query = "SELECT * FROM vw_attendance_report LIMIT 100" # Limit for PDF safety
    filename = f"attendance_report.{format}"
    if format == 'csv':
        export_to_csv(query, filename)
    elif format == 'pdf':
        export_to_pdf(query, "Attendance Report", filename)
