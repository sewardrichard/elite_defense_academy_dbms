import os
import csv
import json
import random
from faker import Faker

# Initialize Faker with consistent locale
fake = Faker(['zu_ZA', 'en_GB'])

# Directory setup
RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), '../docs/data/raw')
os.makedirs(RAW_DATA_DIR, exist_ok=True)

def generate_messy_student_csv(filename='students_raw.csv', n=50):
    """
    Generate a CSV file with intentional 'messy' data to test ETL cleaning logic.
    
    Issues introduced:
    - Missing emails
    - Invalid email formats
    - Uppercase/lowercase inconsistencies in names
    - Duplicate entries
    """
    filepath = os.path.join(RAW_DATA_DIR, filename)
    print(f"Generating messy CSV: {filepath}")
    
    headers = ['Full Name', 'Email Address', 'Phone_Num', 'DOB', 'Rank']
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for _ in range(n):
            # 1. Generate core data
            fn = fake.first_name()
            ln = fake.last_name()
            
            # 2. Introduce "messiness"
            
            # Name formatting issues (all caps, all lower)
            if random.random() < 0.2:
                full_name = f"{fn.upper()} {ln.lower()}"
            else:
                full_name = f"{fn} {ln}"
                
            # Email issues
            rand_val = random.random()
            if rand_val < 0.1:
                email = "" # Missing email
            elif rand_val < 0.2:
                email = f"{fn}@{ln}" # Invalid format
            else:
                email = f"{fn}.{ln}@{fake.domain_name()}"
                
            # Phone issues (inconsistent formats)
            if random.random() < 0.3:
                phone = fake.basic_phone_number() # Random format
            else:
                phone = f"0{fake.random_int(60, 89)} {fake.random_int(100, 999)} {fake.random_int(1000, 9999)}" # Standard local
                
            dob = fake.date_of_birth(minimum_age=18, maximum_age=35).isoformat()
            rank = random.choice(['Recruit', 'Cadet', 'Private', 'Unknown'])
            
            writer.writerow([full_name, email, phone, dob, rank])
            
        # Add a deliberate duplicate row for testing deduplication using specific values
        writer.writerow(["John Doe", "john.doe@example.com", "082 123 4567", "2000-01-01", "Recruit"])
        writer.writerow(["John Doe", "john.doe@example.com", "082 123 4567", "2000-01-01", "Recruit"])

    print(f"Created {filename} with ~{n} rows.")

def generate_courses_json(filename='courses_catalog.json', n=10):
    """
    Generate a JSON file representing an external course catalog.
    """
    filepath = os.path.join(RAW_DATA_DIR, filename)
    print(f"Generating JSON catalog: {filepath}")
    
    courses = []
    departments = ['Cybersecurity', 'Logistics', 'Medical', 'Aviation']
    
    for _ in range(n):
        dept = random.choice(departments)
        course = {
            "course_code": f"{dept[:3].upper()}-{fake.random_int(800, 999)}", # New range
            "course_title": f"{dept} {fake.word().capitalize()} Fundamentals",
            "department": dept,
            "credits": random.randint(2, 4),
            "difficulty": random.choice(['Basic', 'Intermediate']),
            "description": fake.sentence(nb_words=10)
        }
        courses.append(course)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(courses, f, indent=4)
        
    print(f"Created {filename} with {n} courses.")

def generate_messy_grades_csv(filename='grades_raw.csv', n=100):
    """Generate raw assessment data with missing values and bad formats."""
    filepath = os.path.join(RAW_DATA_DIR, filename)
    headers = ['Student_Email', 'Course_Code', 'Assessment', 'Raw_Score', 'Weight', 'Date']
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for _ in range(n):
            score = random.uniform(30, 100) if random.random() > 0.1 else "" # Missing values
            date = fake.date_this_year().strftime("%d/%m/%Y") if random.random() > 0.2 else fake.date_this_year().isoformat()
            writer.writerow([
                fake.email(), 
                f"TAC-{random.randint(100, 110)}", 
                random.choice(['Quiz', 'Exam', 'Final']), 
                score, 
                0.2, 
                date
            ])
    print(f"Created {filename}")

def generate_messy_attendance_csv(filename='attendance_raw.csv', n=100):
    """Generate raw attendance logs."""
    filepath = os.path.join(RAW_DATA_DIR, filename)
    headers = ['Email', 'Course', 'MusterDate', 'Status']
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for _ in range(n):
            writer.writerow([
                fake.email(),
                f"TAC-{random.randint(100, 110)}",
                fake.date_this_month().isoformat(),
                random.choice(['Present', 'Absent', 'Late', 'Excused', 'UNK'])
            ])
    print(f"Created {filename}")

if __name__ == "__main__":
    generate_messy_student_csv()
    generate_courses_json()
    generate_messy_grades_csv()
    generate_messy_attendance_csv()
