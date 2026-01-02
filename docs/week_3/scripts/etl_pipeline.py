import os
import pandas as pd
import json
import psycopg2
from psycopg2 import OperationalError, extras
import re
from datetime import datetime
import logging
import random

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
        logger.error(f"DB Error: {e}")
        return None

def extract_data():
    """PHASE 1: EXTRACT"""
    logger.info("Extracting data from sources...")
    
    try:
        df_students = pd.read_csv(os.path.join(RAW_DATA_DIR, 'students_raw.csv'))
        with open(os.path.join(RAW_DATA_DIR, 'courses_catalog.json'), 'r') as f:
            df_courses = pd.DataFrame(json.load(f))
        df_grades = pd.read_csv(os.path.join(RAW_DATA_DIR, 'grades_raw.csv'))
        df_attendance = pd.read_csv(os.path.join(RAW_DATA_DIR, 'attendance_raw.csv'))
        
        logger.info(f"Extracted {len(df_students)} students, {len(df_courses)} courses, "
                    f"{len(df_grades)} grades, {len(df_attendance)} attendance records.")
        return df_students, df_courses, df_grades, df_attendance
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return None, None, None, None

def transform_data(df_students, df_courses, df_grades, df_attendance):
    """PHASE 2: TRANSFORM"""
    logger.info("Transforming data...")
    
    # 1. Standardize Dates
    for df in [df_students, df_grades, df_attendance]:
        for col in ['DOB', 'Date', 'MusterDate']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d')
    
    # 2. Student Cleaning
    df_students['Email Address'] = df_students['Email Address'].str.strip().str.lower()
    df_students.dropna(subset=['Email Address'], inplace=True)
    df_students['Full Name'] = df_students['Full Name'].str.title()
    df_students[['first_name', 'last_name']] = df_students['Full Name'].str.split(' ', n=1, expand=True)
    
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    df_students = df_students[df_students['Email Address'].str.match(email_pattern, na=False)].copy()
    
    # 3. GPA Calculation (Mock logic for raw data)
    df_grades['Raw_Score'] = pd.to_numeric(df_grades['Raw_Score'], errors='coerce')
    df_grades.dropna(subset=['Raw_Score'], inplace=True)
    
    # Simple GPA: Score / 25 (0-4 scale)
    student_stats = df_grades.groupby('Student_Email')['Raw_Score'].mean().reset_index()
    student_stats['gpa'] = (student_stats['Raw_Score'] / 25).round(2)
    
    # 4. Attendance Categorization
    df_attendance['is_present'] = df_attendance['Status'].isin(['Present', 'Late'])
    att_stats = df_attendance.groupby('Email')['is_present'].mean().reset_index()
    att_stats['att_rate'] = (att_stats['is_present'] * 100).round(2)
    
    def get_standing(rate):
        if rate >= 90: return 'Honor Roll'
        if rate >= 70: return 'Good Standing'
        return 'Academic Warning'
    att_stats['standing'] = att_stats['att_rate'].apply(get_standing)
    
    # --- COURSE TRANSFORMATION ---
    # Rename columns to match DB schema
    df_courses = df_courses.rename(columns={
        'course_title': 'name',
        'difficulty': 'difficulty_level'
    })
    
    logger.info("Transformation complete.")
    return df_students, df_courses, student_stats, att_stats

def load_data(conn, df_students, df_courses, df_stats, df_att):
    """PHASE 3: LOAD (Batch)"""
    logger.info("Loading data into DB...")
    
    try:
        with conn.cursor() as cur:
            # Get default company
            cur.execute("SELECT company_id FROM companies LIMIT 1")
            res = cur.fetchone()
            if not res:
                logger.error("No companies found in DB. Run generate_sample_data.py first.")
                return
            company_id = res[0]
            
            # 1. Batch Load Students
            student_data = [
                (company_id, f"SN-{random.randint(2000, 9999)}", row['first_name'], row['last_name'], 
                 row['Email Address'], row['DOB'], row['Rank'])
                for _, row in df_students.iterrows()
            ]
            extras.execute_batch(cur, """
                INSERT INTO students (company_id, service_number, first_name, last_name, email, date_of_birth, rank)
                VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (email) DO NOTHING
            """, student_data)
            
            # 2. Batch Load Courses
            course_data = [
                (r['course_code'], r['name'], r['credits'], r['department'], r['difficulty_level'], r['description'])
                for _, r in df_courses.iterrows()
            ]
            extras.execute_batch(cur, """
                INSERT INTO courses (course_code, name, credits, department, difficulty_level, description)
                VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (course_code) DO NOTHING
            """, course_data)
            
            # 3. Batch Update Summaries (Linking stats & analytics)
            # This requires student_id mapping if we want to be exact, 
            # for this mock we update based on email matches.
            cur.execute("SELECT student_id, email FROM students")
            email_map = dict(cur.fetchall())
            
            summary_data = []
            for _, row in df_stats.iterrows():
                email = row['Student_Email']
                if email in email_map:
                    sid = email_map[email]
                    att_row = df_att[df_att['Email'] == email]
                    rate = att_row['att_rate'].values[0] if not att_row.empty else 100.0
                    std = att_row['standing'].values[0] if not att_row.empty else 'Good Standing'
                    summary_data.append((sid, row['gpa'], rate, std))
            
            extras.execute_batch(cur, """
                INSERT INTO performance_summary (student_id, gpa, attendance_rate, current_standing)
                VALUES (%s, %s, %s, %s) 
                ON CONFLICT (student_id) DO UPDATE SET 
                    gpa = EXCLUDED.gpa, attendance_rate = EXCLUDED.attendance_rate
            """, summary_data)
            
        conn.commit()
        logger.info("Batch Load Successful.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Load failed, rolling back. Error: {e}")

def main():
    import random # for service numbers
    conn = create_connection()
    if conn:
        s, c, g, a = extract_data()
        if s is not None:
            s_clean, c_clean, stats, atts = transform_data(s, c, g, a)
            load_data(conn, s_clean, c_clean, stats, atts)
        conn.close()

if __name__ == "__main__":
    main()
