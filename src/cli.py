import sys
from datetime import date
import os
from src.controllers import (
    add_student, enroll_student, record_grade, mark_attendance, 
    update_student, delete_student, get_student_id_by_email, get_student_details,
    get_students_in_course,
    get_student_enrollments, get_student_grades, get_student_attendance,
    update_grade, delete_grade, update_attendance, delete_attendance,
    get_all_courses, add_course, update_course, delete_course, unenroll_student
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
        
    details = get_student_details(sid)
    if details:
        print(f"\n--- Current Details for {details.get('first_name')} {details.get('last_name')} ---")
        print(f"ID: {details.get('student_id')}")
        print(f"Name: {details.get('first_name')} {details.get('last_name')}")
        print(f"Email: {details.get('email')}")
        print(f"DOB: {details.get('date_of_birth')}")
        print(f"Gender: {details.get('gender')}")
        print(f"Rank: {details.get('rank')}")
        print("-----------------------------------")
    
    print("Leave fields blank to keep current value.")
    
    c_first = f" [{details['first_name']}]" if details else ""
    first = get_user_input(f"First Name{c_first}", required=False)
    if first is None: return
    
    c_last = f" [{details['last_name']}]" if details else ""
    last = get_user_input(f"Last Name{c_last}", required=False)
    if last is None: return
    
    c_email = f" [{details['email']}]" if details else ""
    new_email = get_user_input(f"New Email{c_email}", validator=validate_email, required=False)
    if new_email is None: return
    
    c_dob = f" [{details['date_of_birth']}]" if details else ""
    dob = get_user_input(f"Date of Birth (YYYY-MM-DD){c_dob}", validator=validate_date, required=False)
    if dob is None: return
    
    c_gender = f" [{details['gender']}]" if details else ""
    gender = None
    while True:
        gender_input = get_user_input(f"Gender (M/F){c_gender}", required=False)
        if gender_input is None: return
        if not gender_input:
            break
        
        g_val = gender_input.lower()[0]
        if g_val == 'm':
            gender = 'Male'
            break
        elif g_val == 'f':
            gender = 'Female'
            break
        else:
            print("Invalid selection. Only 'Male' and 'Female' are accepted.")
    
    c_rank = f" [{details['rank']}]" if details else ""
    rank = get_user_input(f"Rank{c_rank}", required=False)
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
    
    details = get_student_details(sid)
    if details:
        print(f"\n--- Student Details ---")
        print(f"ID: {sid}")
        print(f"Name: {details.get('first_name')} {details.get('last_name')}")
        print(f"Email: {details.get('email')}")
        print(f"Gender: {details.get('gender')}")
        print(f"Rank: {details.get('rank')}")
        print("-----------------------")
    else:
        print(f"Student ID: {sid}")
        
    confirm = get_user_input(f"Are you sure you want to delete this student? (y/n)")
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
        print("q. Back")
        
        choice = input("\nSelect Option: ").strip().lower()
        
        if choice == '1':
            perform_add_student()
        elif choice == '2':
            # Pagination & Search Logic
            offset = 0
            limit = 10
            search_term = None
            
            while True:
                params = []
                base_query = "SELECT student_id, first_name, last_name, email, rank FROM students"
                
                if search_term:
                    base_query += " WHERE first_name ILIKE %s OR last_name ILIKE %s OR email ILIKE %s OR rank ILIKE %s OR CAST(student_id AS TEXT) ILIKE %s"
                    p = f"%{search_term}%"
                    params = [p, p, p, p, p]
                    header = f"Search Results for '{search_term}'"
                else:
                    header = "All Students"
                
                query = base_query + f" ORDER BY student_id LIMIT {limit} OFFSET {offset}"
                
                print(f"\n--- {header} (Rows {offset+1} to {offset+limit}) ---")
                res = execute_query(query, tuple(params), fetch=True)
                
                if res:
                    print_results(res)
                else:
                    if offset == 0:
                        print("No records found.")
                    else:
                        print("No more records.")
                
                # Navigation Menu
                nav_opts = ["[s] Search", "[q] Back"]
                if search_term:
                    nav_opts.insert(1, "[c] Clear Search")
                if res and len(res) == limit:
                    nav_opts.insert(0, "[Enter] Next Page")
                
                print("\nOptions: " + " | ".join(nav_opts))
                nav = input("Select Action: ").strip().lower()
                
                if nav == 'q':
                    break
                elif nav == 's':
                    term = input("Enter search term: ").strip()
                    if term:
                        search_term = term
                        offset = 0
                elif nav == 'c' and search_term:
                    search_term = None
                    offset = 0
                elif nav == '':
                    # Next page request
                    if res and len(res) == limit:
                        offset += limit
                    else:
                        print("End of list.")
                else:
                    pass # Just refresh
                
        elif choice == '3':
            perform_update_student()
        elif choice == '4':
            perform_delete_student()
        elif choice == 'q':
            return
        else:
            print("Invalid selection.")

def menu_reports():
    while True:
        print("\n--- Generate Reports ---")
        print("1. Student Roster")
        print("2. Attendance Report")
        print("q. Back")
        
        choice = input("\nSelect Report: ").strip().lower()
        
        if choice == 'q': return
        
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
        print("q. Back")
        
        choice = input("\nSelect Option: ").strip().lower()
        
        if choice == 'q': return
        
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

def perform_add_course():
    print("\n--- Add New Course ---")
    
    code = get_user_input("Course Code (e.g. WPN-202)")
    if code is None: return
    
    name = get_user_input("Course Name")
    if name is None: return
    
    credits_in = get_user_input("Credits (1-20)")
    if credits_in is None: return
    try:
        credits = int(credits_in)
    except:
        print("Invalid credits.")
        return
        
    dept = get_user_input("Department")
    if dept is None: return
    
    diff = get_user_input("Difficulty (Basic/Intermediate/Advanced)", required=False) or "Basic"
    desc = get_user_input("Description", required=False)
    
    add_course(code, name, credits, dept, diff, desc)
    input("Press Enter to continue...")

def perform_course_action_with_student_selection(course_code, action_type):
    """
    Generic helper to select a student from a course and perform an action (Grade/Attendance).
    Paginated list of enrolled students.
    """
    students = get_students_in_course(course_code)
    if not students:
        print("No students enrolled in this course.")
        return

    offset = 0
    limit = 10
    
    while True:
        # Slice for pagination
        page_items = students[offset:offset+limit]
        
        print(f"\n--- Select Student for {action_type} (Page {offset//limit + 1}) ---")
        for i, s in enumerate(page_items, 1):
             print(f"{s['student_id']}. {s['first_name']} {s['last_name']} ({s['email']})")
             
        print("\nOptions:")
        print(" - Enter Student ID to Select")
        print(" - [Enter] Next Page")
        print(" - [q] Back")
        
        choice = input("Choice: ").strip()
        
        if choice.lower() == 'q':
            return
            
        if choice == "":
            if offset + limit < len(students):
                offset += limit
            else:
                 offset = 0
                 print("Restarting list...")
            continue
            
        # Try to match ID
        try:
            sid_input = int(choice)
            selected_student = next((s for s in students if s['student_id'] == sid_input), None)
            if selected_student:
                # Perform Action
                if action_type == "Grade":
                     perform_add_grade_context(selected_student['email'], course_code)
                elif action_type == "Attendance":
                     perform_mark_attendance_context(selected_student['email'], course_code)
                return # Return to course menu after action
            else:
                print("Invalid Student ID from list.")
        except ValueError:
            print("Invalid input.")

def perform_add_grade_context(email, course_code):
    print(f"\nAdding Grade for {email} in {course_code}")
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
    record_grade(email, course_code, atype, float(score), w_float, remarks)
    input("Press Enter to continue...")

def perform_mark_attendance_context(email, course_code):
    print(f"\nMarking Attendance for {email} in {course_code}")
    dt = get_user_input("Date (YYYY-MM-DD)", validator=validate_date) or str(date.today())
    if dt is None: return

    status = get_user_input("Status (Present/Absent/Late/Excused)")
    if status is None: return
    
    remarks = get_user_input("Remarks", required=False)
    mark_attendance(email, course_code, dt, status, remarks)
    input("Press Enter to continue...")

def perform_manage_course(course):
    """Sub-menu for a specific course."""
    cid = course['course_id']
    ccode = course['course_code']
    
    while True:
        print(f"\n--- Managing Course: {ccode} - {course['name']} ---")
        print("1. Enroll Student")
        print("2. Unenroll Student")
        print("3. Record Grade")
        print("4. Mark Attendance")
        print("5. Update Course Details")
        print("6. Delete Course")
        print("0. Back")
        
        choice = input("\nSelect Option: ").strip()
        
        if choice == '1':
            email = get_user_input("Student Email", validator=validate_email)
            if email:
                date_str = str(date.today())
                enroll_student(email, ccode, date_str)
                input("Press Enter to continue...")
        elif choice == '2':
            email = get_user_input("Student Email", validator=validate_email)
            if email:
                confirm = get_user_input(f"Unenroll {email} from {ccode}? (y/n)")
                if confirm and confirm.lower() == 'y':
                    unenroll_student(email, ccode)
                input("Press Enter to continue...")
        elif choice == '3':
            perform_course_action_with_student_selection(ccode, "Grade")
        elif choice == '4':
            perform_course_action_with_student_selection(ccode, "Attendance")
        elif choice == '5':
             print(f"Update {ccode}. Leave blank to keep current.")
             n_name = get_user_input(f"Name [{course['name']}]", required=False)
             
             n_credits = None
             c_in = get_user_input(f"Credits [{course.get('credits', '')}]", required=False)
             if c_in:
                 try: n_credits = int(c_in)
                 except: print("Invalid credits ignored.")
             
             n_dept = get_user_input(f"Department [{course.get('department','')}]", required=False)
             n_diff = get_user_input(f"Difficulty [{course.get('difficulty_level','')}]", required=False)
             n_desc = get_user_input(f"Description [{course.get('description','')}]", required=False)
             
             if update_course(cid, n_name, n_credits, n_dept, n_diff, n_desc):
                 # Update local view
                 if n_name: course['name'] = n_name
                 if n_credits: course['credits'] = n_credits
                 if n_dept: course['department'] = n_dept
                 if n_diff: course['difficulty_level'] = n_diff
                 if n_desc: course['description'] = n_desc
             input("Press Enter to continue...")
        elif choice == '6':
            confirm = get_user_input(f"Delete course {ccode}? This cannot be undone. (y/n)")
            if confirm and confirm.lower() == 'y':
                if delete_course(cid):
                    input("Deleted. Press Enter...")
                    return # Exit management view as course is gone
            else:
                print("Cancelled.")
        elif choice == 'q':
            return
        else:
            print("Invalid.")

def menu_course_management():
    """List courses and allow management."""
    offset = 0
    limit = 10
    
    while True:
        query = f"SELECT course_id, course_code, name, credits FROM courses ORDER BY course_id LIMIT {limit} OFFSET {offset}"
        courses = execute_query(query, fetch=True)
        
        print(f"\n--- Course Management (Page {offset//limit + 1}) ---")
        if courses:
            for i, c in enumerate(courses, 1):
                print(f"{i}. {c['course_code']} - {c['name']} ({c['credits']} cr)")
        else:
            if offset == 0:
                print("No courses found.")
            else:
                print("No more courses.")
        
        print("\nOptions:")
        print(" - Enter Number to Manage Course")
        print(" - [Enter] Next Page")
        print(" - [a] Add Course")
        print(" - [q] Back")
        
        choice = input("Select: ").strip().lower()
        
        if choice == 'q':
            return
        elif choice == 'a':
            perform_add_course()
        elif choice == '':
            if courses and len(courses) == limit:
                offset += limit
            elif not courses and offset > 0:
                 offset = 0 
                 print("Restarting list...")
            else:
                print("End of list.")
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(courses):
                    perform_manage_course(courses[idx])
                else:
                    print("Invalid selection.")
            except ValueError:
                pass


def main():
    while True:
        print_header()
        print("1. Student Management")
        print("2. Course Management")
        print("3. Generate Reports")
        print("4. Stored Procedures")
        print("q. Exit")
        
        choice = input("\nSelect an option: ").strip().lower()
        
        if choice == '1':
            menu_student_management()
        elif choice == '2':
            menu_course_management()
        elif choice == '3':
            menu_reports()
        elif choice == '4':
            menu_stored_procedures()
        elif choice == 'q':
            print("Exiting...")
            sys.exit(0)
        else:
            print("Invalid choice, please try again.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
