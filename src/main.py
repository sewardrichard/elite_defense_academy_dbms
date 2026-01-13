import argparse
import sys
from src.controllers import add_student, enroll_student, record_grade, mark_attendance
from src.reports import generate_roster_report, generate_attendance_report
from datetime import date

def main():
    parser = argparse.ArgumentParser(description="Elite Defense Academy CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Add Student
    parser_add = subparsers.add_parser('add-student', help='Add a new student')
    parser_add.add_argument('--first', required=True, help='First Name')
    parser_add.add_argument('--last', required=True, help='Last Name')
    parser_add.add_argument('--email', required=True, help='Email Address')
    parser_add.add_argument('--dob', required=True, help='Date of Birth (YYYY-MM-DD)')
    parser_add.add_argument('--gender', default='Male', choices=['Male', 'Female', 'Other'], help='Gender')
    parser_add.add_argument('--rank', default='Recruit', help='Rank')

    # Enroll
    parser_enroll = subparsers.add_parser('enroll', help='Enroll a student in a course')
    parser_enroll.add_argument('--email', required=True, help='Student Email')
    parser_enroll.add_argument('--course', required=True, help='Course Code')
    parser_enroll.add_argument('--date', default=str(date.today()), help='Start Date (YYYY-MM-DD)')

    # Record Grade
    parser_grade = subparsers.add_parser('grade', help='Record a grade')
    parser_grade.add_argument('--email', required=True, help='Student Email')
    parser_grade.add_argument('--course', required=True, help='Course Code')
    parser_grade.add_argument('--type', required=True, help='Assessment Type (Exam, Quiz, etc.)')
    parser_grade.add_argument('--score', required=True, type=float, help='Score (0-100)')
    parser_grade.add_argument('--weight', required=True, type=float, help='Weight (0.0-1.0)')
    parser_grade.add_argument('--remarks', help='Remarks')

    # Mark Attendance
    parser_att = subparsers.add_parser('attendance', help='Mark attendance')
    parser_att.add_argument('--email', required=True, help='Student Email')
    parser_att.add_argument('--course', required=True, help='Course Code')
    parser_att.add_argument('--date', default=str(date.today()), help='Date (YYYY-MM-DD)')
    parser_att.add_argument('--status', required=True, choices=['Present', 'Absent', 'Late', 'AWOL', 'Excused'], help='Status')
    parser_att.add_argument('--remarks', help='Remarks')

    # Reports
    parser_rep = subparsers.add_parser('report', help='Generate reports')
    parser_rep.add_argument('--type', required=True, choices=['roster', 'attendance'], help='Report Type')
    parser_rep.add_argument('--format', default='csv', choices=['csv', 'pdf'], help='Output Format')

    args = parser.parse_args()

    if args.command == 'add-student':
        add_student(args.first, args.last, args.email, args.dob, args.gender, args.rank)
    
    elif args.command == 'enroll':
        enroll_student(args.email, args.course, args.date)
    
    elif args.command == 'grade':
        record_grade(args.email, args.course, args.type, args.score, args.weight, args.remarks)
    
    elif args.command == 'attendance':
        mark_attendance(args.email, args.course, args.date, args.status, args.remarks)
    
    elif args.command == 'report':
        if args.type == 'roster':
            generate_roster_report(args.format)
        elif args.type == 'attendance':
            generate_attendance_report(args.format)
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
