import csv
import random
import os
import uuid
import json
from datetime import datetime, timedelta

# NOTE: This script requires the 'Faker' library.
# Install via: pip install faker
try:
    from faker import Faker
except ImportError:
    print("CRITICAL ERROR: 'Faker' module not found. Run 'pip install faker'")
    exit(1)

# --- CONFIGURATION ---
NUM_COMPANIES = 5
NUM_CADETS = 300
NUM_MODULES = 15
OUTPUT_DIR = "data/raw"

fake = Faker()
Faker.seed(2025)
random.seed(2025)

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Global Storage for Relational Integrity
companies_data = []
cadets_data = []
modules_data = []
records_data = []

def generate_companies():
    print(f"[*] Generating {NUM_COMPANIES} Companies...")
    filename = os.path.join(OUTPUT_DIR, "companies.csv")
    
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['company_id', 'company_code', 'company_name', 'commanding_officer', 'max_strength']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        codes = ['ALPHA', 'BRAVO', 'CHARLIE', 'DELTA', 'ECHO']
        
        for i in range(NUM_COMPANIES):
            c_id = i + 1
            code = codes[i]
            row = {
                'company_id': c_id,
                'company_code': f"{code}-CO",
                'company_name': f"{code} Company",
                'commanding_officer': f"Cpt. {fake.last_name()}",
                'max_strength': 100
            }
            companies_data.append(row)
            writer.writerow(row)

def generate_cadets():
    print(f"[*] Generating {NUM_CADETS} Cadets...")
    filename = os.path.join(OUTPUT_DIR, "cadets.csv")
    
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['cadet_id', 'service_number', 'first_name', 'last_name', 'email', 
                      'dob', 'enrollment_date', 'rank', 'company_id', 'status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for i in range(NUM_CADETS):
            c_id = i + 1
            first = fake.first_name()
            last = fake.last_name()
            company = random.choice(companies_data)
            
            row = {
                'cadet_id': c_id,
                'service_number': f"SN-2025-{str(c_id).zfill(3)}",
                'first_name': first,
                'last_name': last,
                'email': f"{first.lower()}.{last.lower()}@elite.mil",
                'dob': fake.date_of_birth(minimum_age=18, maximum_age=24),
                'enrollment_date': fake.date_between(start_date='-2y', end_date='today'),
                'rank': random.choice(['Recruit', 'Recruit', 'Private', 'Private', 'Corporal']),
                'company_id': company['company_id'],
                'status': random.choice(['Active', 'Active', 'Active', 'Medical Leave'])
            }
            cadets_data.append(row)
            writer.writerow(row)

def generate_modules():
    print(f"[*] Generating {NUM_MODULES} Modules...")
    filename = os.path.join(OUTPUT_DIR, "training_modules.csv")
    
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['module_id', 'module_code', 'name', 'credits', 'department', 'difficulty_level', 'total_sessions']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        depts = ['Cyber', 'Physical', 'Strategic', 'Tactical', 'Medical']
        
        for i in range(NUM_MODULES):
            m_id = i + 1
            dept = random.choice(depts)
            row = {
                'module_id': m_id,
                'module_code': f"{dept[:3].upper()}-{random.randint(100,999)}",
                'name': f"Adv. {dept} Operations {random.randint(1,5)}",
                'credits': random.randint(3, 6),
                'department': dept,
                'difficulty_level': random.choice(['Basic', 'Advanced', 'Elite']),
                'total_sessions': random.randint(10, 30)
            }
            modules_data.append(row)
            writer.writerow(row)

def generate_service_records_and_evals():
    print(f"[*] Generating Service Records & Evals...")
    
    rec_file = os.path.join(OUTPUT_DIR, "service_records.csv")
    eval_file = os.path.join(OUTPUT_DIR, "performance_evals.csv")
    
    with open(rec_file, 'w', newline='') as rf, open(eval_file, 'w', newline='') as ef:
        rec_writer = csv.DictWriter(rf, fieldnames=['record_id', 'cadet_id', 'module_id', 'start_date', 
                                                    'completion_date', 'status', 'final_score', 'grade_letter'])
        eval_writer = csv.DictWriter(ef, fieldnames=['eval_id', 'record_id', 'assessment_name', 'score', 
                                                     'weight', 'evaluation_date'])
        
        rec_writer.writeheader()
        eval_writer.writeheader()
        
        rec_id_counter = 1
        eval_id_counter = 1
        
        for cadet in cadets_data:
            # Assign 3-6 random modules to each cadet
            assigned_modules = random.sample(modules_data, k=random.randint(3, 6))
            
            for mod in assigned_modules:
                start_dt = cadet['enrollment_date'] + timedelta(days=random.randint(1, 60))
                is_complete = random.random() > 0.2
                
                final_score = round(random.uniform(50, 100), 2)
                grade = 'F'
                if final_score >= 90: grade = 'A'
                elif final_score >= 80: grade = 'B'
                elif final_score >= 70: grade = 'C'
                elif final_score >= 60: grade = 'D'
                
                rec_row = {
                    'record_id': rec_id_counter,
                    'cadet_id': cadet['cadet_id'],
                    'module_id': mod['module_id'],
                    'start_date': start_dt,
                    'completion_date': start_dt + timedelta(days=60) if is_complete else None,
                    'status': 'Completed' if is_complete else 'Active',
                    'final_score': final_score if is_complete else None,
                    'grade_letter': grade if is_complete else None
                }
                
                records_data.append(rec_row)
                rec_writer.writerow(rec_row)
                
                # Generate Evals for this record
                num_evals = random.randint(2, 4)
                for _ in range(num_evals):
                    eval_row = {
                        'eval_id': eval_id_counter,
                        'record_id': rec_id_counter,
                        'assessment_name': random.choice(['Midterm', 'Final', 'Practical', 'Drill']),
                        'score': round(random.uniform(60, 100), 2),
                        'weight': 0.25,
                        'evaluation_date': start_dt + timedelta(days=random.randint(5, 50))
                    }
                    eval_writer.writerow(eval_row)
                    eval_id_counter += 1
                
                rec_id_counter += 1

def generate_risk_and_summary():
    print(f"[*] Generating Analytics Data (Risk/Summary)...")
    
    risk_file = os.path.join(OUTPUT_DIR, "attrition_risk.csv")
    
    with open(risk_file, 'w', newline='') as rf:
        fieldnames = ['risk_id', 'cadet_id', 'risk_score', 'risk_level', 'risk_factors']
        writer = csv.DictWriter(rf, fieldnames=fieldnames)
        writer.writeheader()
        
        risk_id = 1
        for cadet in cadets_data:
            # 20% of cadets have high risk
            is_risky = random.random() < 0.2
            score = random.randint(70, 99) if is_risky else random.randint(10, 40)
            level = 'Critical' if score > 85 else ('High' if score > 70 else 'Low')
            
            row = {
                'risk_id': risk_id,
                'cadet_id': cadet['cadet_id'],
                'risk_score': score,
                'risk_level': level,
                'risk_factors': json.dumps({"attendance_issues": is_risky, "medical_flags": random.randint(0,2)})
            }
            writer.writerow(row)
            risk_id += 1

if __name__ == "__main__":
    generate_companies()
    generate_cadets()
    generate_modules()
    generate_service_records_and_evals()
    generate_risk_and_summary() # Includes Muster Rolls conceptual logic in factors
    print(f"\n[SUCCESS] Generated 5 related CSV files in {os.path.abspath(OUTPUT_DIR)}")
