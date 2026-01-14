import unittest
from unittest.mock import patch, MagicMock
from src.utils import validate_email, validate_score, validate_date
from src.controllers import add_student, enroll_student
import os

class TestUtils(unittest.TestCase):
    def test_validate_email(self):
        self.assertTrue(validate_email("test@example.com"))
        self.assertFalse(validate_email("invalid-email"))
        self.assertFalse(validate_email("user@domain")) # missing TLD

    def test_validate_score(self):
        self.assertTrue(validate_score(50))
        self.assertTrue(validate_score("99.9"))
        self.assertFalse(validate_score(-1))
        self.assertFalse(validate_score(101))
        self.assertFalse(validate_score("abc"))

    def test_validate_date(self):
        self.assertTrue(validate_date("2023-01-01"))
        self.assertFalse(validate_date("01-01-2023")) # Wrong format
        self.assertFalse(validate_date("2023/01/01"))

class TestControllers(unittest.TestCase):
    @patch('src.controllers.execute_query')
    def test_add_student_success(self, mock_query):
        # Mocking successful insertion returning an ID
        mock_query.return_value = [{'student_id': 123}]
        
        # We also need to mock get_default_company_id which calls execute_query
        # The first call is for company_id, second for insert
        mock_query.side_effect = [[{'company_id': 1}], [{'student_id': 123}]]
        
        result = add_student("Test", "Cadet", "test@eda.mil", "2000-01-01")
        self.assertTrue(result)

    @patch('src.controllers.execute_proc')
    @patch('src.controllers.get_student_id_by_email')
    @patch('src.controllers.get_course_id_by_code')
    def test_enroll_student_success(self, mock_get_course, mock_get_student, mock_proc):
        mock_get_student.return_value = 1
        mock_get_course.return_value = 101
        mock_proc.return_value = 500 # enrollment_id
        
        result = enroll_student("test@eda.mil", "TAC-101", "2023-01-01")
        self.assertTrue(result)

    @patch('src.controllers.get_student_id_by_email')
    def test_enroll_student_not_found(self, mock_get_student):
        mock_get_student.return_value = None # Student not found
        result = enroll_student("ghost@eda.mil", "TAC-101", "2023-01-01")
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
