import os
import random
import argparse
from datetime import datetime, timedelta
from faker import Faker
import psycopg2
from psycopg2 import OperationalError

# Initialize Faker with fallback
try:
    # zu_ZA (Zulu South Africa) is available and appropriate. 
    # en_GB provides a good mix for English names common# Initialize Faker with fallback
    fake = Faker(['zu_ZA', 'en_GB'])
    fake_en = Faker('en_GB') # Dedicated English provider for descriptions
except Exception as e:
    print(f"Warning: Could not initialize South African locale ({e}). Falling back to default.")
    fake = Faker()
    fake_en = Faker()

# Manual lists for South African / Zimbabwean flavor if Faker defaults are too generic
SA_FIRST_NAMES = ["Thabo", "Sipho", "Bongani", "Nandi", "Lerato", "Zanele", "Pieter", "Johan", "Willem", "Riaan", "Tendai", "Farai", "Nyasha", "Kudakwashe", "Tinashe"]
SA_LAST_NAMES = ["Nkosi", "Khumalo", "Molefe", "Dlamini", "Ndlovu", "Van der Merwe", "Botha", "Venter", "Coetzee", "Naidoo", "Pillay", "Patel", "Moyo", "Ncube", "Sibanda"]

def get_regional_name():
    """Generate a name with a mix of Faker and manual regional names."""
    if random.random() < 0.6: # 60% chance to use specific regional names
        fn = random.choice(SA_FIRST_NAMES) if random.random() > 0.5 else fake.first_name()
        ln = random.choice(SA_LAST_NAMES) if random.random() > 0.5 else fake.last_name()
        return fn, ln
    return fake.first_name(), fake.last_name()

def generate_sa_phone():
    """Generate a South African phone number: +27 XX XXX XXXX"""
    # Common prefixes: 082, 072, 061 etc (dropping leading 0 for intl format)
    prefix = random.choice(['60', '61', '62', '63', '71', '72', '73', '74', '76', '78', '79', '81', '82', '83', '84'])
    return f"+27 {prefix} {fake.random_number(digits=3, fix_len=True)} {fake.random_number(digits=4, fix_len=True)}"

def load_env_from_file():
    """Load key=value pairs from project root .env if present (non-fatal if missing)."""
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..", ".env"))
    if not os.path.isfile(env_path):
        return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            if k and v and k not in os.environ:
                os.environ[k] = v


def require_env(key: str, default: str = None):
    val = os.getenv(key, default)
    if val is None:
        raise ValueError(f"Missing required environment variable: {key}. Set it in .env")
    return val


# Database Configuration (pulled from .env or process env)
load_env_from_file()
DB_NAME = require_env("DB_NAME", "student_records_db")
DB_USER = require_env("DB_USER")
DB_PASSWORD = require_env("DB_PASSWORD")
DB_HOST = require_env("DB_HOST", "localhost")
DB_PORT = require_env("DB_PORT", "5432")

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

def clear_data(conn):
    """Clears existing data to allow fresh generation."""
    cursor = conn.cursor()
    print("WARNING: Clearing existing data from tables...")
    tables = ["attrition_risk", "performance_summary", "attendance", "grades", "enrollments", "students", "companies", "courses"]
    for table in tables:
        # Using DELETE instead of TRUNCATE ... RESTART IDENTITY because the latter
        # requires ownership of the sequences, which srms_admin_user might not have.
        cursor.execute(f"DELETE FROM {table};")
    conn.commit()
    print("Data cleared.")

def generate_companies(conn, n=5, dry_run=False):
    if dry_run: 
        print(f"\n[Preview] Generating {n} companies (Dry Run):")
    else:
        print(f"Generating {n} companies...")
        
    cursor = conn.cursor()
    companies = []
    
    for i in range(n):
        company = {
            "name": f"Company {fake.unique.word().capitalize()} {fake.random_int(1,99)}",
            "location": fake.address().replace('\n', ', '),
            "officer": get_regional_name()[0] + " " + get_regional_name()[1] # Use consistent naming
        }
        
        if dry_run:
            print(f"  - {company['name']} | Cmd: {company['officer']}")
            companies.append(i) # Dummy IDs for dry run
        else:
            try:
                cursor.execute(
                    "INSERT INTO companies (company_name, location, commanding_officer) VALUES (%s, %s, %s) RETURNING company_id",
                    (company["name"], company["location"], company["officer"])
                )
                companies.append(cursor.fetchone()[0])
            except Exception:
                conn.rollback()
                continue

    if not dry_run: conn.commit()
    return companies

def generate_students(conn, company_ids, n=500, dry_run=False):
    if dry_run:
        print(f"\n[Preview] Generating {n} students (Sample of first 5):")
        
    cursor = conn.cursor()
    student_ids = []
    
    # Custom Zim/SA name additions could go here if Faker isn't enough, 
    # but en_ZA is usually sufficient.
    
    for i in range(n):
        f_name, l_name = get_regional_name()
        student = {
            "cid": random.choice(company_ids) if company_ids else 1,
            "sn": f"SN-{random.randint(2020, 2025)}-{fake.unique.random_number(digits=4)}",
            "fn": f_name,
            "ln": l_name,
            "dob": fake.date_of_birth(minimum_age=18, maximum_age=30),
            "gen": random.choice(['Male', 'Female']),
            "phone": generate_sa_phone(),
            "email": f"{f_name.lower()}.{l_name.lower()}@{fake.domain_name()}",
            "addr": fake.address().replace('\n', ', '),
            "rank": random.choice(['Recruit', 'Cadet', 'Private']),
            "status": 'Active'
        }

        if dry_run:
            if i < 5: # Only show first 5
                print(f"  - {student['sn']} | {student['fn']} {student['ln']} | {student['phone']} | {student['email']}")
            student_ids.append(i)
        else:
            try:
                cursor.execute(
                    """
                    INSERT INTO students (
                        company_id, service_number, first_name, last_name, 
                        date_of_birth, gender, contact_number, email, address, rank, status
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
                    RETURNING student_id
                    """,
                    (student['cid'], student['sn'], student['fn'], student['ln'], student['dob'], 
                     student['gen'], student['phone'], student['email'], student['addr'], student['rank'], student['status'])
                )
                student_ids.append(cursor.fetchone()[0])
            except Exception:
                conn.rollback()
                continue
                
    if not dry_run: 
        conn.commit()
        print(f"Inserted {len(student_ids)} students.")
    return student_ids

def generate_courses(conn, n=30, dry_run=False):
    cursor = conn.cursor()
    course_ids = []
    if not dry_run: print(f"Generating {n} courses...")
    
    depts = ['Tactics', 'Engineering', 'Leadership', 'Weapons', 'Intelligence']
    for i in range(n):
        dept = random.choice(depts)
        c_code = f"{dept[:3].upper()}-{fake.unique.random_number(digits=3)}"
        c_name = f"{dept} {fake_en.word().capitalize()} {fake.random_int(1,5)}" # English word
        c_desc = fake_en.text(max_nb_chars=200) # Force English Description
        
        if dry_run and i < 3:
             print(f"  - Course: {c_code} | {c_name} | {c_desc[:50]}...")
        
        if not dry_run:
            try:
                cursor.execute(
                    """
                    INSERT INTO courses (course_code, name, credits, department, difficulty_level, description)
                    VALUES (%s, %s, %s, %s, %s, %s) RETURNING course_id
                    """,
                    (c_code, c_name, random.randint(1, 5), dept, random.choice(['Basic', 'Intermediate', 'Advanced']), c_desc)
                )
                course_ids.append(cursor.fetchone()[0])
            except Exception:
                conn.rollback()
                continue
        else:
            course_ids.append(i)
            
    if not dry_run: conn.commit()
    return course_ids

def enroll_students(conn, student_ids, course_ids, dry_run=False):
    if dry_run: return
    
    cursor = conn.cursor()
    print("Enrolling students & generating history...")
    count = 0
    for sid in student_ids:
        for cid in random.sample(course_ids, k=random.randint(3, 5)):
            start = fake.date_between(start_date='-1y', end_date='-6m')
            
            # To avoid NULLs, we make all enrollments "Completed" or at least 
            # have a status that implies non-null scores even if failed.
            # "In Progress" would imply NULLs for completion_date.
            # So we will force Completed/Failed/Withdrawn but all with dates.
            
            # 90% Completed/Failed, 10% Withdrawn
            is_withdrawn = random.random() < 0.1
            
            if is_withdrawn:
                 completion_date = start + timedelta(days=random.randint(10, 30))
                 final_score = 0.0 # Or keep NULL? User said "no null values". 
                 # Schema allows NULL for Withdrawn usually, but to strictly follow "No Nulls"...
                 # We will set score to 0.0 and Grade to 'F' or None?
                 # Let's just make everything "Completed" or "Failed" to be safe and logical.
                 is_withdrawn = False # Override for simplicity of "No Nulls"
            
            # Force everything to be "done"
            completion_date = start + timedelta(days=random.randint(30, 90))
            final_score = round(random.uniform(40, 100), 2)
            
            grade = 'F'
            if final_score >= 90: grade = 'A'
            elif final_score >= 80: grade = 'B'
            elif final_score >= 70: grade = 'C'
            elif final_score >= 60: grade = 'D'
            
            status = 'Completed' if final_score >= 60 else 'Failed'
            
            try:
                cursor.execute(
                    """
                    INSERT INTO enrollments (student_id, course_id, start_date, completion_date, final_score, grade_letter, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING enrollment_id
                    """,
                    (sid, cid, start, completion_date, final_score, grade, status)
                )
                eid = cursor.fetchone()[0]
                count += 1
                
                # Grades with Remarks
                for atype, w in [('Quiz', 0.2), ('Assignment', 0.3), ('Exam', 0.5)]:
                    # Generate some remarks to avoid NULLs
                    remark = fake_en.sentence(nb_words=6)
                    cursor.execute(
                        "INSERT INTO grades (enrollment_id, assessment_type, score, weight, remarks) VALUES (%s, %s, %s, %s, %s)",
                        (eid, atype, round(random.uniform(60, 100), 2), w, remark)
                    )
                
                # Attendance with Remarks and Recorder
                curr = start
                for _ in range(10):
                    if curr > datetime.now().date(): break
                    att_status = random.choice(['Present', 'Present', 'Absent', 'Late'])
                    remark = "On time" if att_status == 'Present' else fake_en.sentence(nb_words=3)
                    recorded_by = "Sgt. " + fake.last_name()
                    
                    cursor.execute(
                        """
                        INSERT INTO attendance (student_id, course_id, muster_date, status, remarks, recorded_by) 
                        VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING
                        """,
                        (sid, cid, curr, att_status, remark, recorded_by)
                    )
                    curr += timedelta(days=1)
            except Exception:
                conn.rollback()
                continue
    conn.commit()
    print(f"Created {count} enrollments.")

def generate_analytics(conn, student_ids, dry_run=False):
    if dry_run: return
    
    cursor = conn.cursor()
    print("Generating analytics (Performance & Risk)...")
    summary_count, risk_count = 0, 0
    
    for sid in student_ids:
        try:
            cursor.execute("""
                SELECT AVG(final_score), SUM(c.credits)
                FROM enrollments e
                JOIN courses c ON e.course_id = c.course_id
                WHERE e.student_id = %s
            """, (sid,))
            avg_score, total_credits = cursor.fetchone()
            
            gpa = 0.0
            if avg_score:
                gpa = min(4.0, max(0.0, (float(avg_score) - 50) / 10))
            
            total_credits = total_credits or 0
            
            cursor.execute("""
                SELECT COUNT(*) FILTER (WHERE status = 'Present'), COUNT(*)
                FROM attendance WHERE student_id = %s
            """, (sid,))
            present, total_days = cursor.fetchone()
            att_rate = (present / total_days * 100) if total_days and total_days > 0 else 100.0
            
            standing = 'Good Standing'
            if gpa < 2.0: standing = 'Academic Warning'
            if att_rate < 70: standing = 'Probation'
            if gpa > 3.5: standing = 'Deans List'
            
            cursor.execute("""
                INSERT INTO performance_summary (student_id, gpa, attendance_rate, total_credits, current_standing)
                VALUES (%s, %s, %s, %s, %s) ON CONFLICT (student_id) DO NOTHING
            """, (sid, gpa, att_rate, total_credits, standing))
            summary_count += 1
            
            risk_score = 0
            if gpa < 2.0: risk_score += 40
            if att_rate < 80: risk_score += 30
            if total_credits < 5: risk_score += 10
            risk_score = min(100, risk_score + random.randint(0, 20))
            
            risk_level = 'Low'
            if risk_score > 30: risk_level = 'Medium'
            if risk_score > 60: risk_level = 'High'
            if risk_score > 80: risk_level = 'Critical'
            
            cursor.execute("""
                INSERT INTO attrition_risk (student_id, risk_score, risk_level, contributing_factors, model_version)
                VALUES (%s, %s, %s, %s, 'v1.0')
            """, (sid, risk_score, risk_level, f"GPA: {gpa:.2f}, Attendance: {att_rate:.1f}%"))
            risk_count += 1
        except Exception:
            conn.rollback()
            continue
            
    conn.commit()
    print(f"Generated {summary_count} summaries and {risk_count} risk assessments.")

def main():
    parser = argparse.ArgumentParser(description="Generate Sample Data for SRMS")
    parser.add_argument("--dry-run", action="store_true", help="Preview data without inserting into DB")
    parser.add_argument("--clean", action="store_true", help="Clear existing data before generating")
    args = parser.parse_args()

    conn = create_connection()
    if not conn: return
    
    try:
        if args.clean and not args.dry_run:
            clear_data(conn)
        
        c_ids = generate_companies(conn, dry_run=args.dry_run)
        s_ids = generate_students(conn, c_ids, dry_run=args.dry_run)
        course_ids = generate_courses(conn, dry_run=args.dry_run)
        
        if s_ids and course_ids:
            enroll_students(conn, s_ids, course_ids, dry_run=args.dry_run)
            generate_analytics(conn, s_ids, dry_run=args.dry_run)
            
        if args.dry_run:
            print("\n[INFO] Dry Run Complete. No data was inserted.")
            print("Run without --dry-run to commit to database.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
