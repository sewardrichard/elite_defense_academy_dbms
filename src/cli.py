import sys
from datetime import date
from src.controllers import add_student, enroll_student, record_grade, mark_attendance
from src.reports import generate_roster_report, generate_attendance_report
from src.utils import get_user_input, validate_email, validate_date, validate_score

def print_header():
    print("\n" + "="*40)
    print("   ELITE DEFENSE ACADEMY DBMS")
    print("="*40)

def menu_add_student():
    print("\n--- Add New Student ---")
    
    first = get_user_input("First Name")
    if first is None: return

    last = get_user_input("Last Name")
    if last is None: return

    email = get_user_input("Email", validator=validate_email)
    if email is None: return

    dob = get_user_input("Date of Birth (YYYY-MM-DD)", validator=validate_date)
    if dob is None: return

    # Gender selection
    while True:
        gender_input = get_user_input("Gender (M/F/O)")
        if gender_input is None: return
        g_map = {'m': 'Male', 'f': 'Female', 'o': 'Other'}
        gender = g_map.get(gender_input.lower()[0]) if gender_input else None
        if gender:
            break
        print("Invalid selection.")

    rank = get_user_input("Rank", required=False) or "Recruit"
    if rank is None: return

    print(f"\nAdding student: {first} {last}...")
    add_student(first, last, email, dob, gender, rank)
    input("Press Enter to continue...")

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

def menu_grade():
    print("\n--- Record Grade ---")
    email = get_user_input("Student Email", validator=validate_email)
    if email is None: return

    course = get_user_input("Course Code")
    if course is None: return

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
    if remarks is None: return

    record_grade(email, course, atype, float(score), w_float, remarks)
    input("Press Enter to continue...")

def menu_attendance():
    print("\n--- Mark Attendance ---")
    email = get_user_input("Student Email", validator=validate_email)
    if email is None: return

    course = get_user_input("Course Code")
    if course is None: return

    dt = get_user_input("Date (YYYY-MM-DD)", validator=validate_date) or str(date.today())
    if dt is None: return

    status = get_user_input("Status (Present/Absent/Late/Excused)")
    if status is None: return
    # Basic validation could be improved here
    
    remarks = get_user_input("Remarks", required=False)
    if remarks is None: return

    mark_attendance(email, course, dt, status, remarks)
    input("Press Enter to continue...")

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

def main():
    while True:
        print_header()
        print("1. Add Student")
        print("2. Enroll Student")
        print("3. Record Grade")
        print("4. Mark Attendance")
        print("5. Generate Reports")
        print("0. Exit")
        
        choice = input("\nSelect an option: ").strip()
        
        if choice == '1':
            menu_add_student()
        elif choice == '2':
            menu_enroll()
        elif choice == '3':
            menu_grade()
        elif choice == '4':
            menu_attendance()
        elif choice == '5':
            menu_reports()
        elif choice == '0':
            print("Exiting...")
            sys.exit(0)
        else:
            print("Invalid choice, please try again.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
