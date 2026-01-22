import sys
from datetime import date
import os
from src.controllers import (
    add_student, enroll_student, record_grade, mark_attendance, 
    update_student, delete_student, get_student_id_by_email,
    get_student_enrollments, get_student_grades, get_student_attendance,
    update_grade, delete_grade, update_attendance, delete_attendance
)
from src.database import execute_query
from src.reports import generate_roster_report, generate_attendance_report
from src.utils import get_user_input, validate_email, validate_date, validate_score

def print_header():
    print("\n" + "="*40)
    print("   ELITE DEFENSE ACADEMY DBMS")
    print("="*40)

def perform_add_student():
    print("\n--- Add New Student ---")
    
    first = get_user_input("First Name")
    if first is None: return

    last = get_user_input("Last Name")
    if last is None: return

    email = get_user_input("Email", validator=validate_email)
    if email is None: return

    dob = get_user_input("Date of Birth (YYYY-MM-DD)", validator=validate_date)
    if dob is None: return

    while True:
        gender_input = get_user_input("Gender (M/F)")
        if gender_input is None: return
        g_map = {'m': 'Male', 'f': 'Female'}
        gender = g_map.get(gender_input.lower()[0]) if gender_input else None
        if gender:
            break
        print("Invalid selection. Please enter 'M' or 'F'.")

    # Rank selection menu
    ranks = ["Recruit", "Cadet", "Officer Cadet", "Lieutenant", "Captain"]
    print("\nSelect Rank:")
    for i, r in enumerate(ranks, 1):
        print(f"{i}. {r}")
    
    while True:
        r_sel = get_user_input("Rank Choice (1-5)", required=False)
        if r_sel is None: return # Cancel
        if r_sel == "":
            rank = "Recruit" # Default
            break
        try:
            ridx = int(r_sel) - 1
            if 0 <= ridx < len(ranks):
                rank = ranks[ridx]
                break
            print("Invalid number.")
        except:
            print("Invalid input.")

    print(f"\nAdding student: {first} {last}...")
    add_student(first, last, email, dob, gender, rank)
    input("Press Enter to continue...")

def perform_update_student():
    print("\n--- Update Student ---")
    email = get_user_input("Enter Student Email to search")
    if email is None: return
    
    sid = get_student_id_by_email(email)
    if not sid:
        print("Student not found.")
        input("Press Enter to continue...")
        return
        
    print(f"Found Student ID: {sid}. Leave fields blank to keep current value.")
    
    first = get_user_input("First Name", required=False)
    if first is None: return
    
    last = get_user_input("Last Name", required=False)
    if last is None: return
    
    new_email = get_user_input("New Email", validator=validate_email, required=False)
    if new_email is None: return
    
    dob = get_user_input("Date of Birth (YYYY-MM-DD)", validator=validate_date, required=False)
    if dob is None: return
    
    gender = None
    gender_input = get_user_input("Gender (M/F/O)", required=False)
    if gender_input is None: return
    if gender_input:
        g_map = {'m': 'Male', 'f': 'Female', 'o': 'Other'}
        gender = g_map.get(gender_input.lower()[0])
    
    rank = get_user_input("Rank", required=False)
    if rank is None: return
    
    update_student(sid, first, last, new_email, dob, gender, rank)
    input("Press Enter to continue...")

def perform_delete_student():
    print("\n--- Delete Student ---")
    email = get_user_input("Enter Student Email to delete")
    if email is None: return
    
    sid = get_student_id_by_email(email)
    if not sid:
        print("Student not found.")
        input("Press Enter to continue...")
        return
        
    confirm = get_user_input(f"Are you sure you want to delete student ID {sid}? (y/n)")
    if confirm and confirm.lower() == 'y':
        delete_student(sid)
    else:
        print("Deletion cancelled.")
    input("Press Enter to continue...")

def menu_student_management():
    while True:
        print("\n--- Student Management (CRUD) ---")
        print("1. Add Student (Create)")
        print("2. List Students (Read)")
        print("3. Update Student")
        print("4. Delete Student")
        print("0. Back")
        
        choice = input("\nSelect Option: ").strip()
        
        if choice == '1':
            perform_add_student()
        elif choice == '2':
            # Pagination Logic
            offset = 0
            limit = 10
            while True:
                print(f"\nFetching student list (Rows {offset+1} to {offset+limit})...")
                query = f"SELECT student_id, first_name, last_name, email, rank FROM students ORDER BY student_id LIMIT {limit} OFFSET {offset}"
                res = execute_query(query, fetch=True)
                
                if not res and offset == 0:
                    print("No students found.")
                    input("Press Enter to continue...")
                    break
                
                if not res:
                    print("No more records.")
                    input("Press Enter to continue...")
                    break
                    
                print_results(res)
                
                if len(res) < limit:
                    # End of list
                    input("End of list. Press Enter to continue...")
                    break
                    
                nav = input("Press Enter for next page, or 'q' to exit view: ").strip().lower()
                if nav == 'q':
                    break
                offset += limit
                
        elif choice == '3':
            perform_update_student()
        elif choice == '4':
            perform_delete_student()
        elif choice == '0':
            return
        else:
            print("Invalid selection.")

def menu_enroll():
    print("\n--- Enroll Student ---")
    email = get_user_input("Student Email", validator=validate_email)
    if email is None: return

    course = get_user_input("Course Code (e.g. TAC-101)")
    if course is None: return

    start_date = get_user_input("Start Date (YYYY-MM-DD)", validator=validate_date) or str(date.today())
    if start_date is None: return

    enroll_student(email, course, start_date)
    input("Press Enter to continue...")

def select_student_course_context(action_name):
    """Helper to select student and course for grading/attendance."""
    print(f"\n--- {action_name} ---")
    email = get_user_input("Student Email")
    if email is None: return None, None

    enrollments = get_student_enrollments(email)
    if not enrollments:
        print("Student has no active enrollments or does not exist.")
        return None, None

    print(f"\nActive Enrollments for {email}:")
    for idx, enr in enumerate(enrollments):
        print(f"{idx+1}. {enr['course_code']} - {enr['name']} ({enr['status']})")
    
    while True:
        sel = get_user_input("Select Course #", required=True)
        if sel is None: return None, None
        try:
            idx = int(sel) - 1
            if 0 <= idx < len(enrollments):
                course_code = enrollments[idx]['course_code']
                return email, course_code
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")

def perform_add_grade():
    email, course = select_student_course_context("Add Grade")
    if not email: return

    print(f"\nAdding Grade for {email} in {course}")
    atype = get_user_input("Assessment Type (Exam, Quiz, etc)")
    if atype is None: return

    score = get_user_input("Score (0-100)", validator=validate_score)
    if score is None: return

    weight = get_user_input("Weight (0.0 - 1.0)")
    if weight is None: return
    try:
        w_float = float(weight)
    except:
        print("Invalid weight.")
        return

    remarks = get_user_input("Remarks", required=False)
    record_grade(email, course, atype, float(score), w_float, remarks)
    input("Press Enter to continue...")

def perform_view_grades():
    email, course = select_student_course_context("View Grades")
    if not email: return
    
    print(f"\nGrades for {email} in {course}:")
    grades = get_student_grades(email, course)
    print_results(grades)
    input("Press Enter to continue...")

def perform_update_grade():
    email, course = select_student_course_context("Update Grade")
    if not email: return
    
    grades = get_student_grades(email, course)
    if not grades:
        print("No grades found.")
        input("Press Enter to continue...")
        return
        
    print_results(grades)
    gid_input = get_user_input("Enter Grade ID to update")
    if gid_input is None: return
    
    # Verify ID belongs to list
    if not any(str(g['grade_id']) == gid_input for g in grades):
        print("Invalid Grade ID from list.")
        return

    print("Leave blank to keep current value.")
    score = get_user_input("New Score (0-100)", validator=validate_score, required=False)
    
    weight_input = get_user_input("New Weight (0.0 - 1.0)", required=False)
    weight = float(weight_input) if weight_input else None
    
    remarks = get_user_input("New Remarks", required=False)
    
    update_grade(gid_input, score, weight, remarks)
    input("Press Enter to continue...")

def perform_delete_grade():
    email, course = select_student_course_context("Delete Grade")
    if not email: return
    
    grades = get_student_grades(email, course)
    if not grades:
        print("No grades found.")
        input("Press Enter to continue...")
        return
        
    print_results(grades)
    gid_input = get_user_input("Enter Grade ID to delete")
    if gid_input is None: return
    
    if not any(str(g['grade_id']) == gid_input for g in grades):
        print("Invalid Grade ID from list.")
        return

    confirm = get_user_input("Are you sure? (y/n)")
    if confirm and confirm.lower() == 'y':
        delete_grade(gid_input)
    input("Press Enter to continue...")

def menu_grade_management():
    while True:
        print("\n--- Grade Management ---")
        print("1. Record Grade (Create)")
        print("2. View Grades (Read)")
        print("3. Update Grade")
        print("4. Delete Grade")
        print("0. Back")
        
        choice = input("\nSelect Option: ").strip()
        
        if choice == '1':
            perform_add_grade()
        elif choice == '2':
            perform_view_grades()
        elif choice == '3':
            perform_update_grade()
        elif choice == '4':
            perform_delete_grade()
        elif choice == '0':
            return
        else:
            print("Invalid selection.")

def perform_mark_attendance():
    email, course = select_student_course_context("Mark Attendance")
    if not email: return

    dt = get_user_input("Date (YYYY-MM-DD)", validator=validate_date) or str(date.today())
    if dt is None: return

    status = get_user_input("Status (Present/Absent/Late/Excused)")
    if status is None: return
    
    remarks = get_user_input("Remarks", required=False)
    mark_attendance(email, course, dt, status, remarks)
    input("Press Enter to continue...")

def perform_view_attendance():
    email, course = select_student_course_context("View Attendance")
    if not email: return
    
    print(f"\nAttendance for {email} in {course}:")
    recs = get_student_attendance(email, course)
    print_results(recs)
    input("Press Enter to continue...")

def perform_update_attendance():
    email, course = select_student_course_context("Update Attendance")
    if not email: return
    
    recs = get_student_attendance(email, course)
    if not recs:
        print("No records found.")
        input("Press Enter to continue...")
        return
        
    print_results(recs)
    aid_input = get_user_input("Enter Attendance ID to update")
    if aid_input is None: return
    
    if not any(str(r['attendance_id']) == aid_input for r in recs):
        print("Invalid ID.")
        return

    print("Leave blank to keep current value.")
    status = get_user_input("New Status (Present/Absent/Late/Excused)", required=False)
    remarks = get_user_input("New Remarks", required=False)
    
    update_attendance(aid_input, status, remarks)
    input("Press Enter to continue...")

def perform_delete_attendance():
    email, course = select_student_course_context("Delete Attendance")
    if not email: return
    
    recs = get_student_attendance(email, course)
    if not recs:
        print("No records found.")
        input("Press Enter to continue...")
        return
        
    print_results(recs)
    aid_input = get_user_input("Enter Attendance ID to delete")
    if aid_input is None: return
    
    if not any(str(r['attendance_id']) == aid_input for r in recs):
        print("Invalid ID.")
        return

    confirm = get_user_input("Are you sure? (y/n)")
    if confirm and confirm.lower() == 'y':
        delete_attendance(aid_input)
    input("Press Enter to continue...")

def menu_attendance_management():
    while True:
        print("\n--- Attendance Management ---")
        print("1. Mark Attendance (Create)")
        print("2. View Attendance (Read)")
        print("3. Update Attendance")
        print("4. Delete Attendance")
        print("0. Back")
        
        choice = input("\nSelect Option: ").strip()
        
        if choice == '1':
            perform_mark_attendance()
        elif choice == '2':
            perform_view_attendance()
        elif choice == '3':
            perform_update_attendance()
        elif choice == '4':
            perform_delete_attendance()
        elif choice == '0':
            return
        else:
            print("Invalid selection.")

def menu_reports():
    while True:
        print("\n--- Generate Reports ---")
        print("1. Student Roster")
        print("2. Attendance Report")
        print("0. Back")
        
        choice = input("\nSelect Report: ").strip()
        
        if choice == '0': return
        
        fmt = get_user_input("Format (csv/pdf)")
        if fmt is None: return
        if fmt.lower() not in ['csv', 'pdf']:
            print("Invalid format. Defaulting to CSV.")
            fmt = 'csv'

        if choice == '1':
            generate_roster_report(fmt.lower())
        elif choice == '2':
            generate_attendance_report(fmt.lower())
        else:
            print("Invalid selection.")
            continue
        
        input("Press Enter to continue...")

def get_sql_content(filename):
    """Read SQL content from database directory."""
    try:
        # Resolve path relative to this file
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base_dir, 'database', filename)
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading SQL file {filename}: {e}")
        return None

def print_results(results):
    """Helper to print list of dicts as a basic table."""
    if not results:
        print("No results found.")
        return

    # Get headers
    headers = list(results[0].keys())
    
    # Calculate widths
    widths = {h: len(h) for h in headers}
    for row in results:
        for h in headers:
            val = str(row.get(h, ''))
            widths[h] = max(widths[h], len(val))
    
    # Create format string
    fmt = " | ".join([f"{{:<{widths[h]}}}" for h in headers])
    separator = "-+-".join(["-" * widths[h] for h in headers])
    
    # Print table
    print("\n" + fmt.format(*headers))
    print(separator)
    for row in results:
        values = [str(row.get(h, '')) for h in headers]
        print(fmt.format(*values))
    print(f"\n({len(results)} rows)\n")

def menu_stored_procedures():
    while True:
        print("\n--- Stored Procedures & Views ---")
        print("1. View Students in Course (05)")
        print("2. Course Average Grades (06)")
        print("3. Low Attendance Risk (07)")
        print("4. Top Student Ranking (08)")
        print("5. Enrollment Stats (09)")
        print("0. Back")
        
        choice = input("\nSelect Option: ").strip()
        
        if choice == '0': return
        
        sql_file = None
        params = None
        
        if choice == '1':
            course_code = get_user_input("Enter Course Code (e.g. TAC-101)")
            if course_code is None: continue
            
            raw_sql = get_sql_content("05_view_course_students.sql")
            if raw_sql:
                # Replace hardcoded value in file with parameter placeholder
                sql_file = raw_sql.replace("'TAC-101'", "%s")
                params = (course_code,)
                
        elif choice == '2':
            sql_file = get_sql_content("06_course_avg_grades.sql")
        elif choice == '3':
            sql_file = get_sql_content("07_low_attendance_risk.sql")
        elif choice == '4':
            sql_file = get_sql_content("08_top_student_ranking.sql")
        elif choice == '5':
            sql_file = get_sql_content("09_enrollment_stats.sql")
        else:
            print("Invalid selection.")
            continue

        if sql_file:
            print("\nExecuting query...")
            results = execute_query(sql_file, params, fetch=True)
            print_results(results)
        
        input("Press Enter to continue...")

def main():
    while True:
        print_header()
        print("1. Student Management")
        print("2. Enroll Student")
        print("3. Record Grade")
        print("4. Mark Attendance")
        print("5. Generate Reports")
        print("6. Stored Procedures")
        print("0. Exit")
        
        choice = input("\nSelect an option: ").strip()
        
        if choice == '1':
            menu_student_management()
        elif choice == '2':
            menu_enroll()
        elif choice == '3':
            menu_grade_management()
        elif choice == '4':
            menu_attendance_management()
        elif choice == '5':
            menu_reports()
        elif choice == '6':
            menu_stored_procedures()
        elif choice == '0':
            print("Exiting...")
            sys.exit(0)
        else:
            print("Invalid choice, please try again.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
