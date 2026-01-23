import unittest
import pandas as pd
import numpy as np
from scripts.etl_pipeline import transform_data

class TestETLPipeline(unittest.TestCase):
    def setUp(self):
        # Create mock dataframes similar to what extract_data produces
        
        # 1. Students Raw
        self.df_students = pd.DataFrame({
            'Full Name': ['John Doe', 'JANE SMITH', 'No Email User'],
            'Email Address': ['John.Doe@Example.com', ' jane.smith@test.co.za ', np.nan],
            'DOB': ['2000-01-01', '1999/12/31', '2001-05-05'],
            'Rank': ['Recruit', 'Cadet', 'Private']
        })

        # 2. Courses Raw
        self.df_courses = pd.DataFrame({
            'course_code': ['TAC-101'],
            'course_title': ['Tactics Basics'], # transform renames this to 'name'
            'credits': [3],
            'department': ['Tactics'],
            'difficulty': ['Basic'], # transform renames to 'difficulty_level'
            'description': ['Intro']
        })

        # 3. Grades Raw
        self.df_grades = pd.DataFrame({
            'Student_Email': ['john.doe@example.com', 'john.doe@example.com'],
            'Raw_Score': ['80', '90'],
            'Date': ['2023-01-01', '2023-02-01']
        })

        # 4. Attendance Raw
        self.df_attendance = pd.DataFrame({
            'Email': ['john.doe@example.com', 'john.doe@example.com'],
            'Status': ['Present', 'Absent'],
            'MusterDate': ['2023-01-01', '2023-01-02']
        })

    def test_transform_data(self):
        """Test the transformation logic: cleaning, standardization, and calculations."""
        
        s_clean, c_clean, stats, atts = transform_data(
            self.df_students, 
            self.df_courses, 
            self.df_grades, 
            self.df_attendance
        )

        # 1. Check Student Cleaning
        # - 'No Email User' should be dropped
        self.assertEqual(len(s_clean), 2)
        
        # - Email should be lowercase and stripped
        self.assertTrue('john.doe@example.com' in s_clean['Email Address'].values)
        self.assertTrue('jane.smith@test.co.za' in s_clean['Email Address'].values)
        
        # - Name should be Title Case and split
        row_john = s_clean[s_clean['Email Address'] == 'john.doe@example.com'].iloc[0]
        self.assertEqual(row_john['first_name'], 'John')
        self.assertEqual(row_john['last_name'], 'Doe')
        
        # - Date standardization
        self.assertEqual(row_john['DOB'], '2000-01-01')

        # 2. Check Course Renaming
        self.assertTrue('name' in c_clean.columns)
        self.assertTrue('difficulty_level' in c_clean.columns)
        self.assertEqual(c_clean.iloc[0]['name'], 'Tactics Basics')

        # 3. Check GPA Calculation (Stats)
        # John has scores 80 and 90. Avg = 85.
        # GPA = 85 / 25 = 3.4
        john_stats = stats[stats['Student_Email'] == 'john.doe@example.com']
        self.assertFalse(john_stats.empty)
        self.assertAlmostEqual(john_stats.iloc[0]['gpa'], 3.4)

        # 4. Check Attendance Stats
        # John is Present (1) and Absent (0). Rate = 50%
        john_att = atts[atts['Email'] == 'john.doe@example.com']
        self.assertFalse(john_att.empty)
        self.assertEqual(john_att.iloc[0]['att_rate'], 50.0)
        self.assertEqual(john_att.iloc[0]['standing'], 'Academic Warning')

if __name__ == '__main__':
    unittest.main()
