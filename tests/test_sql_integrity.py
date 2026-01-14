import unittest
from src.database import execute_query

class TestDataIntegrity(unittest.TestCase):
    def test_orphaned_enrollments(self):
        """Check for orphaned enrollments (should be 0)"""
        sql = """
            SELECT COUNT(*) AS count 
            FROM enrollments e 
            LEFT JOIN students s ON s.student_id = e.student_id 
            WHERE s.student_id IS NULL;
        """
        res = execute_query(sql, fetch=True)
        count = res[0]['count']
        self.assertEqual(count, 0, f"Found {count} orphaned enrollments")

    def test_invalid_grades(self):
        """Check for invalid grades (should be 0)"""
        sql = "SELECT COUNT(*) AS count FROM grades WHERE score < 0 OR score > 100;"
        res = execute_query(sql, fetch=True)
        count = res[0]['count']
        self.assertEqual(count, 0, f"Found {count} invalid grades")

    def test_unassigned_students(self):
        """Check for students with NO company assigned"""
        sql = "SELECT count(*) as count FROM students WHERE company_id IS NULL;"
        res = execute_query(sql, fetch=True)
        count = res[0]['count']
        self.assertEqual(count, 0, f"Found {count} students without company")

    def test_duplicate_active_enrollments(self):
        """Check for duplicate active enrollments"""
        sql = """
            SELECT student_id, course_id, COUNT(*) 
            FROM enrollments 
            WHERE status = 'In Progress' 
            GROUP BY student_id, course_id 
            HAVING COUNT(*) > 1;
        """
        res = execute_query(sql, fetch=True)
        # res should be empty
        self.assertEqual(len(res), 0, f"Found duplicate enrollments: {res}")

    def test_email_format(self):
        """Simple regex check on database logic side if needed, or just data check"""
        sql = "SELECT email FROM students WHERE email NOT LIKE '%@%.%';"
        res = execute_query(sql, fetch=True)
        self.assertEqual(len(res), 0, f"Found invalid emails: {res}")

if __name__ == '__main__':
    unittest.main()
