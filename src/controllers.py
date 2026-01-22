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

def get_all_courses():
    """Retrieve all available courses."""
    return execute_query("SELECT course_id, course_code, name, description FROM courses ORDER BY course_id", fetch=True)

def get_default_company_id():
    """Get the first company ID found in DB."""
    res = execute_query("SELECT company_id FROM companies LIMIT 1", fetch=True)
    return res[0]['company_id'] if res else None

def get_student_details(student_id):
    """Get full student details by ID."""
    query = "SELECT * FROM students WHERE student_id = %s"
    res = execute_query(query, (student_id,), fetch=True)
    return res[0] if res else None

def get_students_in_course(course_code):
    """Get all students enrolled in a course."""
    cid = get_course_id_by_code(course_code)
    if not cid: return None
    
    query = """
        SELECT s.student_id, s.first_name, s.last_name, s.email, s.rank, e.enrollment_id 
        FROM enrollments e
        JOIN students s ON e.student_id = s.student_id
        WHERE e.course_id = %s
        ORDER BY s.last_name, s.first_name
    """
    return execute_query(query, (cid,), fetch=True)

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

def update_student(student_id, first_name=None, last_name=None, email=None, dob=None, gender=None, rank=None):
    """Update student details."""
    updates = []
    params = []
    
    if first_name:
        updates.append("first_name = %s")
        params.append(first_name)
    if last_name:
        updates.append("last_name = %s")
        params.append(last_name)
    if email:
        updates.append("email = %s")
        params.append(email)
    if dob:
        updates.append("date_of_birth = %s")
        params.append(dob)
    if gender:
        updates.append("gender = %s")
        params.append(gender)
    if rank:
        updates.append("rank = %s")
        params.append(rank)
        
    if not updates:
        print("No changes provided.")
        return False
        
    updates.append("updated_at = CURRENT_TIMESTAMP")
    
    query = f"UPDATE students SET {', '.join(updates)} WHERE student_id = %s"
    params.append(student_id)
    
    try:
        execute_query(query, tuple(params), commit=True)
        print(f"Student {student_id} updated successfully.")
        return True
    except Exception as e:
        print(f"Error updating student: {e}")
        return False

def delete_student(student_id):
    """Delete a student by ID."""
    # Note: This might fail if there are foreign key constraints without cascade.
    # We will attempt to delete and catch errors.
    query = "DELETE FROM students WHERE student_id = %s"
    try:
        execute_query(query, (student_id,), commit=True)
        print(f"Student {student_id} deleted successfully.")
        return True
    except Exception as e:
        print(f"Error deleting student (check for enrolled courses/records): {e}")
        return False

def get_student_enrollments(email):
    """Get list of courses a student is enrolled in."""
    sid = get_student_id_by_email(email)
    if not sid:
        return None
    
    query = """
        SELECT c.course_code, c.name, e.status, e.final_score
        FROM enrollments e
        JOIN courses c ON e.course_id = c.course_id
        WHERE e.student_id = %s
    """
    return execute_query(query, (sid,), fetch=True)

def get_student_grades(email, course_code):
    """Get grades for a specific student and course."""
    enrollment_id = get_enrollment_id(email, course_code)
    if not enrollment_id:
        return None
        
    query = """
        SELECT grade_id, assessment_type, score, weight, assessment_date, remarks
        FROM grades
        WHERE enrollment_id = %s
        ORDER BY assessment_date DESC
    """
    return execute_query(query, (enrollment_id,), fetch=True)

def update_grade(grade_id, score=None, weight=None, remarks=None):
    """Update a specific grade entry."""
    updates = []
    params = []
    
    if score is not None:
        updates.append("score = %s")
        params.append(score)
    if weight is not None:
        updates.append("weight = %s")
        params.append(weight)
    if remarks is not None:
        updates.append("remarks = %s")
        params.append(remarks)
        
    if not updates:
        return False
        
    query = f"UPDATE grades SET {', '.join(updates)} WHERE grade_id = %s"
    params.append(grade_id)
    
    try:
        execute_query(query, tuple(params), commit=True)
        print(f"Grade {grade_id} updated.")
        return True
    except Exception as e:
        print(f"Error updating grade: {e}")
        return False

def delete_grade(grade_id):
    """Delete a grade entry."""
    try:
        execute_query("DELETE FROM grades WHERE grade_id = %s", (grade_id,), commit=True)
        print(f"Grade {grade_id} deleted.")
        return True
    except Exception as e:
        print(f"Error deleting grade: {e}")
        return False

def get_student_attendance(email, course_code):
    """Get attendance records for a student in a course."""
    sid = get_student_id_by_email(email)
    cid = get_course_id_by_code(course_code)
    if not sid or not cid:
        return None
        
    query = """
        SELECT attendance_id, muster_date, status, remarks
        FROM attendance
        WHERE student_id = %s AND course_id = %s
        ORDER BY muster_date DESC
    """
    return execute_query(query, (sid, cid), fetch=True)

def update_attendance(attendance_id, status=None, remarks=None):
    """Update attendance record."""
    updates = []
    params = []
    
    if status:
        updates.append("status = %s")
        params.append(status)
    if remarks is not None:
        updates.append("remarks = %s")
        params.append(remarks)
        
    if not updates:
        return False
        
    updates.append("updated_at = CURRENT_TIMESTAMP")
    query = f"UPDATE attendance SET {', '.join(updates)} WHERE attendance_id = %s"
    params.append(attendance_id)
    
    try:
        execute_query(query, tuple(params), commit=True)
        print(f"Attendance {attendance_id} updated.")
        return True
    except Exception as e:
        print(f"Error updating attendance: {e}")
        return False

def delete_attendance(attendance_id):
    """Delete attendance record."""
    try:
        execute_query("DELETE FROM attendance WHERE attendance_id = %s", (attendance_id,), commit=True)
        print(f"Attendance {attendance_id} deleted.")
        return True
    except Exception as e:
        print(f"Error deleting attendance: {e}")
        return False

def add_course(course_code, name, credits, department, difficulty='Basic', description=None):
    """Add a new course."""
    query = """
        INSERT INTO courses (course_code, name, credits, department, difficulty_level, description)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING course_id
    """
    try:
        res = execute_query(query, (course_code, name, credits, department, difficulty, description), fetch=True, commit=True)
        if res:
            print(f"Course added: {course_code} - {name}")
            return True
    except Exception as e:
        print(f"Error adding course: {e}")
        return False

def update_course(course_id, name=None, credits=None, department=None, difficulty=None, description=None):
    """Update course details."""
    updates = []
    params = []
    
    if name:
        updates.append("name = %s")
        params.append(name)
    if credits is not None:
        updates.append("credits = %s")
        params.append(credits)
    if department:
        updates.append("department = %s")
        params.append(department)
    if difficulty:
        updates.append("difficulty_level = %s")
        params.append(difficulty)
    if description is not None:
        updates.append("description = %s")
        params.append(description)
        
    if not updates:
        print("No changes provided.")
        return False
        
    updates.append("updated_at = CURRENT_TIMESTAMP")
    query = f"UPDATE courses SET {', '.join(updates)} WHERE course_id = %s"
    params.append(course_id)
    
    try:
        execute_query(query, tuple(params), commit=True)
        print(f"Course {course_id} updated.")
        return True
    except Exception as e:
        print(f"Error updating course: {e}")
        return False

def delete_course(course_id):
    """Delete a course."""
    try:
        execute_query("DELETE FROM courses WHERE course_id = %s", (course_id,), commit=True)
        print(f"Course {course_id} deleted.")
        return True
    except Exception as e:
        print(f"Error deleting course: {e}")
        return False

def unenroll_student(student_email, course_code):
    """Unenroll a student from a course."""
    sid = get_student_id_by_email(student_email)
    cid = get_course_id_by_code(course_code)
    
    if not sid or not cid:
        print("Student or Course not found.")
        return False
        
    try:
        execute_query("DELETE FROM enrollments WHERE student_id = %s AND course_id = %s", (sid, cid), commit=True)
        print(f"Unenrolled {student_email} from {course_code}.")
        return True
    except Exception as e:
        print(f"Error unenrolling student: {e}")
        return False
