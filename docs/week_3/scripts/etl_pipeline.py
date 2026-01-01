import os
import pandas as pd
import json
import psycopg2
from psycopg2 import OperationalError
import re
from datetime import datetime

# Database Configuration
DB_NAME = os.getenv("DB_NAME", "student_records_db")
DB_USER = os.getenv("DB_USER", "srms_admin_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "1102")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_DIR = os.path.join(BASE_DIR, '../../data/raw')

def create_connection():
    """Establish database connection."""
    try:
        conn = psycopg2.connect(
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except OperationalError as e:
        print(f"DB Error: {e}")
        return None

def extract_data():
    """
    PHASE 1: EXTRACT
    Read data from CSV and JSON sources into Pandas DataFrames.
    """
    print("\n--- PHASE 1: EXTRACT ---")
    
    # 1. Read Students CSV
    csv_path = os.path.join(RAW_DATA_DIR, 'students_raw.csv')
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found. Run generate_raw_files.py first.")
        return None, None
        
    df_students = pd.read_csv(csv_path)
    print(f"Extracted {len(df_students)} rows from student CSV.")
    
    # 2. Read Courses JSON
    json_path = os.path.join(RAW_DATA_DIR, 'courses_catalog.json')
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found.")
        return None, None
        
    with open(json_path, 'r') as f:
        courses_data = json.load(f)
    df_courses = pd.DataFrame(courses_data)
    print(f"Extracted {len(df_courses)} courses from JSON catalog.")
    
    return df_students, df_courses

def clean_phone(phone):
    """Normalize phone numbers to +27 format."""
    if not phone: return None
    # Remove non-digit chars
    digits = re.sub(r'\D', '', str(phone))
    
    # Check length and format
    if len(digits) == 10 and digits.startswith('0'):
        # 082 123 4567 -> +27 82 123 4567
        return f"+27 {digits[1:3]} {digits[3:6]} {digits[6:]}"
    elif len(digits) == 11 and digits.startswith('27'):
        # 27821234567 -> +27 82 123 4567
        return f"+27 {digits[2:4]} {digits[4:7]} {digits[7:]}"
    else:
        return None # Invalid format

def transform_data(df_students, df_courses):
    """
    PHASE 2: TRANSFORM
    Clean, validate, and standardize the data.
    """
    print("\n--- PHASE 2: TRANSFORM ---")
    
    # --- STUDENT TRANSFORMATION ---
    
    # 1. Deduplication
    initial_count = len(df_students)
    df_students.drop_duplicates(subset=['Email Address'], inplace=True)
    print(f"Removed {initial_count - len(df_students)} duplicate students.")
    
    # 2. Clean Names (Title Case, Split First/Last)
    # Assumes "First Last" format
    df_students['Full Name'] = df_students['Full Name'].str.strip().str.title()
    df_students[['first_name', 'last_name']] = df_students['Full Name'].str.split(' ', n=1, expand=True)
    
    # 3. Validate Emails
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    valid_emails = df_students['Email Address'].str.match(email_pattern, na=False)
    invalid_count = (~valid_emails).sum()
    print(f"Found {invalid_count} invalid emails. Filtering them out...")
    df_students = df_students[valid_emails].copy()
    
    # 4. Standardize Phones
    df_students['contact_number'] = df_students['Phone_Num'].apply(clean_phone)
    
    # 5. Default Values and Mapping
    df_students['status'] = 'Active'
    # Map raw 'Rank' to allowed values, default to 'Recruit' if unknown
    valid_ranks = ['Recruit', 'Cadet', 'Private']
    df_students['rank'] = df_students['Rank'].apply(lambda x: x if x in valid_ranks else 'Recruit')
    
    # Generate Service Numbers for new students (simple generation for demo)
    # In strict prod, this comes from DB sequence or stricter logic
    df_students['service_number'] = df_students.apply(
        lambda x: f"XY-{random.randint(2024,2026)}-{random.randint(1000,9999)}", axis=1
    )
    
    # --- COURSE TRANSFORMATION ---
    
    # Rename columns to match DB schema
    df_courses = df_courses.rename(columns={
        'course_title': 'name',
        'difficulty': 'difficulty_level'
    })
    
    print(f"Data ready for loading: {len(df_students)} students, {len(df_courses)} courses.")
    return df_students, df_courses

def load_data(conn, df_students, df_courses):
    """
    PHASE 3: LOAD
    Batch insert cleaned data into PostgreSQL.
    """
    print("\n--- PHASE 3: LOAD ---")
    cursor = conn.cursor()
    
    # 1. Load Companies (Ensure at least one exists for assignment)
    # We'll just grab the first available company_id
    cursor.execute("SELECT company_id FROM companies LIMIT 1;")
    res = cursor.fetchone()
    if not res:
        print("Error: No companies found in DB. Please run generate_sample_data.py first.")
        return
    default_company_id = res[0]
    
    # 2. Load Students
    students_loaded = 0
    for _, row in df_students.iterrows():
        try:
            cursor.execute(
                """
                INSERT INTO students (
                    company_id, service_number, first_name, last_name, 
                    email, contact_number, date_of_birth, rank, status, address
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'Unknown Address')
                ON CONFLICT (email) DO NOTHING
                RETURNING student_id
                """,
                (default_company_id, row['service_number'], row['first_name'], 
                 row['last_name'], row['Email Address'], row['contact_number'], 
                 row['DOB'], row['rank'], row['status'])
            )
            if cursor.fetchone():
                students_loaded += 1
        except Exception as e:
            conn.rollback()
            print(f"Failed to load student {row['Email Address']}: {e}")
            continue
            
    conn.commit()
    print(f"Successfully loaded {students_loaded} new students.")

    # 3. Load Courses
    courses_loaded = 0
    for _, row in df_courses.iterrows():
        try:
            cursor.execute(
                """
                INSERT INTO courses (
                    course_code, name, credits, department, difficulty_level, description
                ) VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (course_code) DO NOTHING
                RETURNING course_id
                """,
                (row['course_code'], row['name'], row['credits'], 
                 row['department'], row['difficulty_level'], row['description'])
            )
            if cursor.fetchone():
                courses_loaded += 1
        except Exception as e:
            conn.rollback()
            print(f"Failed to load course {row['course_code']}: {e}")
            continue
            
    conn.commit()
    print(f"Successfully loaded {courses_loaded} new courses.")

def main():
    # 0. Connection
    conn = create_connection()
    if not conn: return
    
    try:
        # 1. Extract
        raw_students, raw_courses = extract_data()
        if raw_students is None: return
        
        # 2. Transform
        clean_students, clean_courses = transform_data(raw_students, raw_courses)
        
        # 3. Load
        load_data(conn, clean_students, clean_courses)
        
    except Exception as e:
        print(f"Pipeline Failed: {e}")
    finally:
        conn.close()
        print("\n--- ETL Pipeline Finished ---")

if __name__ == "__main__":
    # Ensure raw files exist before running logic if simple test required
    import random # Needed for transform
    main()
