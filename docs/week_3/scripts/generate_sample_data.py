import os
import random
from datetime import datetime, timedelta
from faker import Faker
import psycopg2
from psycopg2 import OperationalError

# Initialize Faker
fake = Faker()

# Database Configuration
DB_NAME = os.getenv("DB_NAME", "student_records_db")
DB_USER = os.getenv("DB_USER", "srms_admin_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "1102")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

def create_connection():
    try:
        conn = psycopg2.connect(
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        print("Connected to PostgreSQL DB")
        return conn
    except OperationalError as e:
        print(f"The error '{e}' occurred")
        return None

def generate_companies(conn, n=5):
    cursor = conn.cursor()
    companies = []
    print(f"Generating {n} companies...")
    for _ in range(n):
        try:
            cursor.execute(
                "INSERT INTO companies (company_name, location, commanding_officer) VALUES (%s, %s, %s) RETURNING company_id",
                (f"Company {fake.unique.word().capitalize()} {fake.random_int(1,99)}", fake.address(), fake.name())
            )
            companies.append(cursor.fetchone()[0])
        except Exception:
            conn.rollback()
            continue
    conn.commit()
    print(f"Inserted {len(companies)} companies.")
    return companies

def generate_students(conn, company_ids, n=500):
    cursor = conn.cursor()
    student_ids = []
    print(f"Generating {n} students...")
    for _ in range(n):
        f_name = fake.first_name()
        l_name = fake.last_name()
        try:
            cursor.execute(
                """
                INSERT INTO students (
                    company_id, service_number, first_name, last_name, 
                    date_of_birth, gender, contact_number, email, address, rank, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
                RETURNING student_id
                """,
                (
                    random.choice(company_ids),
                    f"SN-{random.randint(2020, 2025)}-{fake.unique.random_number(digits=4)}",
                    f_name, l_name,
                    fake.date_of_birth(minimum_age=18, maximum_age=30),
                    random.choice(['Male', 'Female']),
                    fake.phone_number()[:20],
                    f"{f_name.lower()}.{l_name.lower()}@{fake.domain_name()}",
                    fake.address(),
                    random.choice(['Recruit', 'Cadet', 'Private']),
                    'Active'
                )
            )
            student_ids.append(cursor.fetchone()[0])
        except Exception:
            conn.rollback()
            continue
    conn.commit()
    print(f"Inserted {len(student_ids)} students.")
    return student_ids

def generate_courses(conn, n=30):
    cursor = conn.cursor()
    course_ids = []
    print(f"Generating {n} courses...")
    depts = ['Tactics', 'Engineering', 'Leadership', 'Weapons', 'Intelligence']
    for _ in range(n):
        dept = random.choice(depts)
        try:
            cursor.execute(
                """
                INSERT INTO courses (course_code, name, credits, department, difficulty_level, description)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING course_id
                """,
                (
                    f"{dept[:3].upper()}-{fake.unique.random_number(digits=3)}",
                    f"{dept} {fake.word().capitalize()} {fake.random_int(1,5)}",
                    random.randint(1, 5),
                    dept,
                    random.choice(['Basic', 'Intermediate', 'Advanced']),
                    fake.text(max_nb_chars=200)
                )
            )
            course_ids.append(cursor.fetchone()[0])
        except Exception:
            conn.rollback()
            continue
    conn.commit()
    print(f"Inserted {len(course_ids)} courses.")
    return course_ids

def enroll_students(conn, student_ids, course_ids):
    cursor = conn.cursor()
    print("Enrolling students & generating history...")
    count = 0
    for sid in student_ids:
        # Enroll in random courses
        for cid in random.sample(course_ids, k=random.randint(3, 5)):
            start = fake.date_between(start_date='-1y', end_date='-6m')
            completed = random.random() < 0.8
            final = round(random.uniform(50, 100), 2) if completed else None
            grade = None
            if final:
                grade = 'A' if final >= 90 else 'B' if final >= 80 else 'C' if final >= 70 else 'D' if final >= 60 else 'F'
            
            try:
                cursor.execute(
                    """
                    INSERT INTO enrollments (student_id, course_id, start_date, completion_date, final_score, grade_letter, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING enrollment_id
                    """,
                    (sid, cid, start, start + timedelta(days=90) if completed else None, final, grade, 'Completed' if completed else 'In Progress')
                )
                eid = cursor.fetchone()[0]
                count += 1
                
                # Grades
                for atype, w in [('Quiz', 0.2), ('Assignment', 0.3), ('Exam', 0.5)]:
                    cursor.execute(
                        "INSERT INTO grades (enrollment_id, assessment_type, score, weight) VALUES (%s, %s, %s, %s)",
                        (eid, atype, round(random.uniform(60, 100), 2), w)
                    )
                
                # Attendance
                curr = start
                for _ in range(10):
                    if curr > datetime.now().date(): break
                    cursor.execute(
                        "INSERT INTO attendance (student_id, course_id, muster_date, status) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",
                        (sid, cid, curr, random.choice(['Present', 'Present', 'Absent', 'Late']))
                    )
                    curr += timedelta(days=1)
            except Exception:
                conn.rollback()
                continue
    conn.commit()
    print(f"Created {count} enrollments.")

def generate_analytics(conn, student_ids):
    """
    Generate performance summaries and attrition risk assessments based on inserted data.
    """
    cursor = conn.cursor()
    print("Generating analytics (Performance & Risk)...")
    
    summary_count = 0
    risk_count = 0
    
    for sid in student_ids:
        try:
            # 1. PERFOMANCE SUMMARY
            # Calculate GPA and Total Credits
            cursor.execute("""
                SELECT AVG(final_score), SUM(c.credits)
                FROM enrollments e
                JOIN courses c ON e.course_id = c.course_id
                WHERE e.student_id = %s AND e.status = 'Completed'
            """, (sid,))
            avg_score, total_credits = cursor.fetchone()
            
            # Simple GPA approx: Score / 20 (roughly 100->5.0, scaled down to 4.0 max logic)
            # Better map: >90=4.0, >80=3.0, >70=2.0, >60=1.0. using raw score for simplicity
            gpa = 0.0
            if avg_score:
                gpa = min(4.0, max(0.0, (float(avg_score) - 50) / 10)) # Rough proxy formula
            
            total_credits = total_credits or 0
            
            # Calculate Attendance Rate
            cursor.execute("""
                SELECT 
                    COUNT(*) FILTER (WHERE status = 'Present'),
                    COUNT(*)
                FROM attendance
                WHERE student_id = %s
            """, (sid,))
            present, total_days = cursor.fetchone()
            att_rate = (present / total_days * 100) if total_days and total_days > 0 else 100.0
            
            # Determine Standing
            standing = 'Good Standing'
            if gpa < 2.0: standing = 'Academic Warning'
            if att_rate < 70: standing = 'Probation'
            if gpa > 3.5: standing = 'Deans List'
            
            cursor.execute("""
                INSERT INTO performance_summary (student_id, gpa, attendance_rate, total_credits, current_standing)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (student_id) DO NOTHING
            """, (sid, gpa, att_rate, total_credits, standing))
            summary_count += 1
            
            # 2. ATTRITION RISK
            # Simple logic: Low GPA or Low Attendance = High Risk
            risk_score = 0
            if gpa < 2.0: risk_score += 40
            if att_rate < 80: risk_score += 30
            if total_credits < 5: risk_score += 10
            
            # Add some randomness
            risk_score += random.randint(0, 20)
            risk_score = min(100, risk_score)
            
            risk_level = 'Low'
            if risk_score > 30: risk_level = 'Medium'
            if risk_score > 60: risk_level = 'High'
            if risk_score > 80: risk_level = 'Critical'
            
            cursor.execute("""
                INSERT INTO attrition_risk (student_id, risk_score, risk_level, contributing_factors)
                VALUES (%s, %s, %s, %s)
            """, (sid, risk_score, risk_level, f"GPA: {gpa:.2f}, Attendance: {att_rate:.1f}%"))
            risk_count += 1
            
        except Exception as e:
            print(f"Error analytics for student {sid}: {e}")
            conn.rollback()
            continue
            
    conn.commit()
    print(f"Generated {summary_count} summaries and {risk_count} risk assessments.")

def main():
    conn = create_connection()
    if not conn: return
    
    try:
        c_ids = generate_companies(conn)
        s_ids = generate_students(conn, c_ids)
        course_ids = generate_courses(conn)
        
        if s_ids and course_ids:
            enroll_students(conn, s_ids, course_ids)
            generate_analytics(conn, s_ids)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
