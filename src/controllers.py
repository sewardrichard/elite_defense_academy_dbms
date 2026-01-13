import random
from src.database import execute_query, execute_proc

def get_student_id_by_email(email):
    """Resolve student email to ID."""
    res = execute_query("SELECT student_id FROM students WHERE email = %s", (email,), fetch=True)
    return res[0]['student_id'] if res else None

def get_course_id_by_code(code):
    """Resolve course code to ID."""
    res = execute_query("SELECT course_id FROM courses WHERE course_code = %s", (code,), fetch=True)
    return res[0]['course_id'] if res else None

def get_default_company_id():
    """Get the first company ID found in DB."""
    res = execute_query("SELECT company_id FROM companies LIMIT 1", fetch=True)
    return res[0]['company_id'] if res else None

def get_enrollment_id(student_email, course_code):
    """Resolve enrollment ID from student email and course code."""
    # We need to join to be sure, or just look up IDs first
    sid = get_student_id_by_email(student_email)
    cid = get_course_id_by_code(course_code)
    
    if not sid or not cid:
        print(f"Error: Could not resolve student ({student_email}) or course ({course_code}).")
        return None
        
    query = """
        SELECT enrollment_id FROM enrollments 
        WHERE student_id = %s AND course_id = %s
    """
    res = execute_query(query, (sid, cid), fetch=True)
    return res[0]['enrollment_id'] if res else None

def add_student(first_name, last_name, email, dob, gender='Male', rank='Recruit'):
    """Insert a new student into the database."""
    company_id = get_default_company_id()
    if not company_id:
        print("Error: No companies found to assign student to.")
        return False
    
    # Generate random service number if one isn't handled by DB (it's not auto-gen, it's NOT NULL)
    service_number = f"SN-{random.randint(10000, 99999)}"
    
    query = """
        INSERT INTO students (company_id, service_number, first_name, last_name, email, date_of_birth, gender, rank)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING student_id;
    """
    try:
        res = execute_query(query, (company_id, service_number, first_name, last_name, email, dob, gender, rank), fetch=True, commit=True)
        if res:
            print(f"Student added successfully: {first_name} {last_name} (ID: {res[0]['student_id']})")
            return True
    except Exception as e:
        print(f"Failed to add student: {e}")
        return False

def enroll_student(email, course_code, start_date):
    """Enroll a student in a course using sp_enroll_student."""
    sid = get_student_id_by_email(email)
    cid = get_course_id_by_code(course_code)
    
    if not sid:
        print(f"Error: Student with email '{email}' not found.")
        return False
    if not cid:
        print(f"Error: Course with code '{course_code}' not found.")
        return False
        
    # sp_enroll_student(p_student_id INT, p_course_id INT, p_start_date DATE) RETURNS INT
    print(f"Enrolling Student ID: {sid} in Course ID: {cid} starting {start_date}...")
    enrollment_id = execute_proc('sp_enroll_student', (sid, cid, start_date), fetch_result=True)
    
    if enrollment_id:
        print(f"Enrollment successful. Enrollment ID: {enrollment_id}")
        return True
    else:
        print("Enrollment failed (possibly already enrolled).")
        return False

def record_grade(email, course_code, assessment_type, score, weight, remarks=None):
    """Record a grade using sp_record_grade."""
    enrollment_id = get_enrollment_id(email, course_code)
    if not enrollment_id:
        print("Error: Active enrollment not found.")
        return False
        
    # sp_record_grade(p_enrollment_id, p_assessment_type, p_score, p_weight, p_assessment_date, p_remarks)
    # Using defaults for date (CURRENT_DATE) so we won't pass it from CLI for simplicity unless needed
    try:
        execute_proc('sp_record_grade', (enrollment_id, assessment_type, score, weight, 'now', remarks))
        print(f"Grade recorded for {email} in {course_code}.")
        return True
    except Exception as e:
        print(f"Error recording grade: {e}")
        return False

def mark_attendance(email, course_code, date, status, remarks=None):
    """Mark attendance using sp_mark_attendance."""
    sid = get_student_id_by_email(email)
    cid = get_course_id_by_code(course_code)
    
    if not sid or not cid:
        print("Error: Student or Course not found.")
        return False
        
    # sp_mark_attendance(p_student_id, p_course_id, p_muster_date, p_status, p_remarks) RETURNS INT
    att_id = execute_proc('sp_mark_attendance', (sid, cid, date, status, remarks), fetch_result=True)
    
    if att_id:
        print(f"Attendance marked. ID: {att_id}")
        return True
    else:
        print("Failed to mark attendance.")
        return False
