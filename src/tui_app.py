from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Static, DataTable, Label, ContentSwitcher, Input
from textual.containers import Container, Vertical, Horizontal
from textual.screen import Screen
from src.database import execute_query
from src.controllers import (
    add_student, update_student, delete_student, get_student_id_by_email,
    get_student_enrollments, record_grade, get_student_grades, mark_attendance, get_student_attendance
)
import os

# Helper to load SQL
def load_sql_query(filename):
    """Load SQL query from the database folder."""
    path = os.path.join("database", filename)
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return f.read()

class Sidebar(Container):
    def compose(self) -> ComposeResult:
        yield Label("EDA DBMS", classes="title")
        yield Button("Home", id="btn_home", classes="-active")
        yield Button("Students", id="btn_students")
        yield Button("Academics", id="btn_academics")
        yield Button("Reports", id="btn_reports")
        yield Button("System", id="btn_system")

class HomeView(Container):
    def compose(self) -> ComposeResult:
        yield Static("Welcome to Elite Defense Academy DBMS", classes="welcome-text")
        yield Static("Select a module from the sidebar to begin.", classes="welcome-text")

class StudentsView(Container):
    def compose(self) -> ComposeResult:
        yield Horizontal(
            Label("Student Management", classes="section-title"),
            Button("List", id="btn_view_list_mode", classes="action-btn"),
            Button("Add", id="btn_add_student_mode", classes="action-btn"),
            Button("Update", id="btn_update_student_mode", classes="action-btn"),
            Button("Delete", id="btn_delete_student_mode", classes="action-btn"),
            classes="toolbar"
        )
        with ContentSwitcher(initial="list_pane", id="students_switcher"):
            # List Pane
            with Vertical(id="list_pane"):
                yield DataTable(id="students_table")
            
            # Add Pane
            with Vertical(id="add_pane", classes="form-container"):
                yield Label("New Student Registration")
                yield Input(placeholder="First Name", id="add_fname")
                yield Input(placeholder="Last Name", id="add_lname")
                yield Input(placeholder="Email", id="add_email")
                yield Input(placeholder="YYYY-MM-DD", id="add_dob")
                yield Input(placeholder="Gender (M/F)", id="add_gender")
                yield Input(placeholder="Rank (Recruit, Cadet, etc)", id="add_rank")
                yield Button("Save Student", id="btn_save_new", variant="primary")
                yield Label("", id="lbl_add_status")

            # Update Pane
            with Vertical(id="update_pane", classes="form-container"):
                yield Label("Update Student")
                yield Input(placeholder="Search by Email", id="upd_search_email")
                yield Button("Search", id="btn_upd_search", variant="default")
                
                # Hidden by default or just empty? We'll just have them there.
                yield Input(placeholder="First Name", id="upd_fname")
                yield Input(placeholder="Last Name", id="upd_lname")
                yield Input(placeholder="New Email", id="upd_email") # To change email
                yield Input(placeholder="YYYY-MM-DD", id="upd_dob")
                yield Input(placeholder="Rank", id="upd_rank")
                
                yield Button("Save Changes", id="btn_save_update", variant="primary")
                yield Label("", id="lbl_upd_status")
                
            # Delete Pane
            with Vertical(id="delete_pane", classes="form-container"):
                yield Label("Delete Student")
                yield Input(placeholder="Enter Email to Delete", id="del_email")
                yield Button("Delete Permanently", id="btn_confirm_delete", variant="error")
                yield Label("", id="lbl_del_status")

    def on_mount(self) -> None:
        table = self.query_one("#students_table", DataTable)
        table.cursor_type = "row"
        self.load_students()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        switcher = self.query_one("#students_switcher", ContentSwitcher)
        
        if btn_id == "btn_view_list_mode":
            self.load_students()
            switcher.current = "list_pane"
        elif btn_id == "btn_add_student_mode":
            switcher.current = "add_pane"
        elif btn_id == "btn_update_student_mode":
            switcher.current = "update_pane"
        elif btn_id == "btn_delete_student_mode":
            switcher.current = "delete_pane"
            
        elif btn_id == "btn_save_new":
            self.save_student()
        elif btn_id == "btn_upd_search":
            self.search_student_for_update()
        elif btn_id == "btn_save_update":
            self.update_student_data()
        elif btn_id == "btn_confirm_delete":
            self.delete_student_data()

    def save_student(self):
        fname = self.query_one("#add_fname", Input).value
        lname = self.query_one("#add_lname", Input).value
        email = self.query_one("#add_email", Input).value
        dob = self.query_one("#add_dob", Input).value
        gender_in = self.query_one("#add_gender", Input).value
        rank_in = self.query_one("#add_rank", Input).value
        lbl = self.query_one("#lbl_add_status", Label)

        if not (fname and lname and email and dob):
            lbl.update("Error: Name, Email, DOB are required.")
            return

        # Gender validation
        gender = 'Male' # Default
        if gender_in:
            if gender_in.lower().startswith('m'): gender = 'Male'
            elif gender_in.lower().startswith('f'): gender = 'Female'
            else:
                lbl.update("Error: Gender must be M or F.")
                return

        rank = rank_in if rank_in else "Recruit"

        success = add_student(fname, lname, email, dob, gender, rank)
        if success:
            lbl.update(f"Success: Added {fname} {lname}")
            for inp in self.query("#add_pane Input"):
                inp.value = ""
        else:
            lbl.update("Error: Failed to add student.")

    def search_student_for_update(self):
        email = self.query_one("#upd_search_email", Input).value
        lbl = self.query_one("#lbl_upd_status", Label)
        
        if not email:
            lbl.update("Please enter an email.")
            return
            
        # We need to fetch details. get_student_id_by_email only returns ID.
        # We need a query here.
        query = "SELECT * FROM students WHERE email = %s"
        res = execute_query(query, (email,), fetch=True)
        
        if res:
            data = res[0]
            self.query_one("#upd_fname", Input).value = str(data['first_name'])
            self.query_one("#upd_lname", Input).value = str(data['last_name'])
            self.query_one("#upd_email", Input).value = str(data['email'])
            self.query_one("#upd_dob", Input).value = str(data['date_of_birth'])
            self.query_one("#upd_rank", Input).value = str(data['rank'])
            lbl.update(f"Found: {data['first_name']} {data['last_name']}")
        else:
            lbl.update("Student not found.")
            
    def update_student_data(self):
        search_email = self.query_one("#upd_search_email", Input).value
        lbl = self.query_one("#lbl_upd_status", Label)
        
        if not search_email:
            lbl.update("Search for a student first.")
            return

        sid = get_student_id_by_email(search_email)
        if not sid:
            lbl.update("Original student record lost. Search again.")
            return
            
        fname = self.query_one("#upd_fname", Input).value
        lname = self.query_one("#upd_lname", Input).value
        new_email = self.query_one("#upd_email", Input).value
        dob = self.query_one("#upd_dob", Input).value
        rank = self.query_one("#upd_rank", Input).value
        
        success = update_student(sid, first_name=fname, last_name=lname, email=new_email, dob=dob, rank=rank)
        if success:
            lbl.update("Update successful.")
            # If email changed, update search box so subsequent saves work
            self.query_one("#upd_search_email", Input).value = new_email
        else:
            lbl.update("Update failed.")

    def delete_student_data(self):
        email = self.query_one("#del_email", Input).value
        lbl = self.query_one("#lbl_del_status", Label)
        
        if not email:
            lbl.update("Please enter an email.")
            return
            
        sid = get_student_id_by_email(email)
        if not sid:
            lbl.update("Student not found.")
            return
            
        success = delete_student(sid)
        if success:
            lbl.update(f"Deleted student {sid}.")
            self.query_one("#del_email", Input).value = ""
        else:
            lbl.update("Delete failed (check dependencies).")

    def load_students(self):
        table = self.query_one("#students_table", DataTable)
        table.clear(columns=True)
        query = "SELECT student_id, service_number, first_name, last_name, rank, company_id FROM students ORDER BY student_id DESC"
        data = execute_query(query, fetch=True)
        if data:
            columns = list(data[0].keys())
            table.add_columns(*columns)
            for row in data:
                table.add_row(*list(row.values()))

class AcademicsView(Container):
    def compose(self) -> ComposeResult:
        yield Horizontal(
            Label("Academic Records", classes="section-title"),
            Button("Grades", id="mode_grades", classes="action-btn"),
            Button("Attendance", id="mode_attendance", classes="action-btn"),
            classes="toolbar"
        )
        
        # Shared input for filtering by student email
        with Vertical(classes="filter-bar"):
            yield Label("Select Student:")
            yield Horizontal(
                Input(placeholder="Student Email", id="acad_email"),
                Button("Load Enrollments", id="btn_load_enrollments"),
                classes="input-row"
            )
            yield Label("", id="acad_status_msg")
            
        with ContentSwitcher(initial="grades_pane", id="academics_switcher"):
            # Grades Pane
            with Vertical(id="grades_pane"):
                yield Label("Select Course to Manage Grades:")
                yield DataTable(id="grades_course_table")
                yield Label("Grade Records:")
                yield DataTable(id="grades_table")
                yield Label("Add Grade:")
                yield Horizontal(
                   Input(placeholder="Type (Exam/Quiz)", id="grd_type"),
                   Input(placeholder="Score", id="grd_score"),
                   Input(placeholder="Weight", id="grd_weight"),
                   Input(placeholder="Remarks", id="grd_remarks"),
                   Button("Add", id="btn_add_grade"),
                   classes="input-row"
                )

            # Attendance Pane
            with Vertical(id="attendance_pane"):
                yield Label("Select Course to Manage Attendance:")
                yield DataTable(id="att_course_table")
                yield Label("Attendance Records:")
                yield DataTable(id="att_table")
                yield Label("Mark Attendance:")
                yield Horizontal(
                   Input(placeholder="Date (YYYY-MM-DD)", id="att_date"),
                   Input(placeholder="Status (Present/Absent)", id="att_status"),
                   Input(placeholder="Remarks", id="att_remarks"),
                   Button("Mark", id="btn_add_att"),
                   classes="input-row"
                )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        switcher = self.query_one("#academics_switcher", ContentSwitcher)
        
        if btn_id == "mode_grades":
            switcher.current = "grades_pane"
        elif btn_id == "mode_attendance":
            switcher.current = "attendance_pane"
        elif btn_id == "btn_load_enrollments":
            self.load_enrollments()
        elif btn_id == "btn_add_grade":
            self.add_grade_entry()
        elif btn_id == "btn_add_att":
            self.add_attendance_entry()

    def load_enrollments(self):
        email = self.query_one("#acad_email", Input).value
        lbl = self.query_one("#acad_status_msg", Label)
        
        if not email:
            lbl.update("Enter an email first.")
            return

        enrollments = get_student_enrollments(email)
        if not enrollments:
            lbl.update("No active enrollments found.")
            return
            
        lbl.update(f"Loaded {len(enrollments)} courses.")
        
        # Populate course tables for both views
        for tid in ["#grades_course_table", "#att_course_table"]:
            table = self.query_one(tid, DataTable)
            table.clear(columns=True)
            table.cursor_type = "row"
            table.add_columns("Code", "Name", "Status")
            for enr in enrollments:
                table.add_row(enr['course_code'], enr['name'], enr['status'])

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        # Determine which table triggered this
        table_id = event.data_table.id
        if table_id not in ["grades_course_table", "#att_course_table"]:
            # If they clicked one of the record tables, ignore for now (could implement update/delete select here)
            pass
            
        # Get course code from selection (Column 0)
        row = event.data_table.get_row_at(event.cursor_row)
        course_code = row[0]
        email = self.query_one("#acad_email", Input).value
        
        if table_id == "grades_course_table":
            self.load_grades(email, course_code)
        elif table_id == "att_course_table":
            self.load_attendance(email, course_code)

    def load_grades(self, email, course_code):
        table = self.query_one("#grades_table", DataTable)
        table.clear(columns=True)
        data = get_student_grades(email, course_code)
        if data:
            columns = list(data[0].keys())
            table.add_columns(*columns)
            for row in data:
                table.add_row(*list(row.values()))
        else:
            table.add_columns("Message")
            table.add_row("No grades recorded.")

    def load_attendance(self, email, course_code):
        table = self.query_one("#att_table", DataTable)
        table.clear(columns=True)
        data = get_student_attendance(email, course_code)
        if data:
            columns = list(data[0].keys())
            table.add_columns(*columns)
            for row in data:
                table.add_row(*list(row.values()))
        else:
            table.add_columns("Message")
            table.add_row("No attendance records.")

    def add_grade_entry(self):
        email = self.query_one("#acad_email", Input).value
        
        # Get selected course from table cursor
        ctable = self.query_one("#grades_course_table", DataTable)
        if ctable.cursor_row is None:
            self.query_one("#acad_status_msg", Label).update("Select a course first.")
            return
            
        row = ctable.get_row_at(ctable.cursor_row)
        course_code = row[0]
        
        atype = self.query_one("#grd_type", Input).value
        score = self.query_one("#grd_score", Input).value
        weight = self.query_one("#grd_weight", Input).value
        remarks = self.query_one("#grd_remarks", Input).value or ""
        
        try:
            record_grade(email, course_code, atype, float(score), float(weight), remarks)
            self.query_one("#acad_status_msg", Label).update("Grade Added.")
            self.load_grades(email, course_code)
        except Exception as e:
            self.query_one("#acad_status_msg", Label).update(f"Error: {e}")

    def add_attendance_entry(self):
        email = self.query_one("#acad_email", Input).value
        
        # Get selected course from table cursor
        ctable = self.query_one("#att_course_table", DataTable)
        if ctable.cursor_row is None:
            self.query_one("#acad_status_msg", Label).update("Select a course first.")
            return
            
        row = ctable.get_row_at(ctable.cursor_row)
        course_code = row[0]
        
        dt = self.query_one("#att_date", Input).value
        status = self.query_one("#att_status", Input).value
        remarks = self.query_one("#att_remarks", Input).value or ""
        
        try:
            mark_attendance(email, course_code, dt, status, remarks)
            self.query_one("#acad_status_msg", Label).update("Attendance Marked.")
            self.load_attendance(email, course_code)
        except Exception as e:
             self.query_one("#acad_status_msg", Label).update(f"Error: {e}")

class ReportsView(Container):
    def compose(self) -> ComposeResult:
        yield Label("Analytics Dashboard", classes="section-title")
        yield Horizontal(
            Vertical(
                Button("Course Performance", id="rep_performance", classes="report-btn"),
                Button("Honor Roll", id="rep_honor", classes="report-btn"),
                Button("Enrollment Stats", id="rep_stats", classes="report-btn"),
                id="report_sidebar",
            ),
            DataTable(id="reports_table"),
            classes="reports-container"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if not btn_id.startswith("rep_"):
            return
            
        table = self.query_one("#reports_table", DataTable)
        table.clear(columns=True)
        
        sql_file = ""
        if btn_id == "rep_performance":
            sql_file = "06_course_avg_grades.sql"
        elif btn_id == "rep_honor":
            sql_file = "08_top_student_ranking.sql"
        elif btn_id == "rep_stats":
            sql_file = "09_enrollment_stats.sql"
            
        if sql_file:
            self.run_report(sql_file, table)
            
    def run_report(self, filename, table):
        query = load_sql_query(filename)
        if not query:
            return
            
        try:
            results = execute_query(query, fetch=True)
            if results:
                columns = list(results[0].keys())
                table.add_columns(*columns)
                for row in results:
                    table.add_row(*list(row.values()))
            else:
                table.add_columns("Result")
                table.add_row("No data found.")
        except Exception as e:
            table.add_columns("Error")
            table.add_row(str(e))

class EDATuiApp(App):
    CSS_PATH = "tui.css"
    BINDINGS = [("d", "toggle_dark", "Toggle Dark Mode"), ("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            Sidebar(id="sidebar"),
            ContentSwitcher(
                HomeView(id="view_home"),
                StudentsView(id="view_students"),
                AcademicsView(id="view_academics"),
                ReportsView(id="view_reports"),
                initial="view_home",
                id="main_content"
            )
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        switcher = self.query_one("#main_content", ContentSwitcher)
        
        # Reset active button styles
        for btn in self.query("#sidebar Button"):
            btn.remove_class("-active")
        event.button.add_class("-active")

        if button_id == "btn_home":
            switcher.current = "view_home"
        elif button_id == "btn_students":
            switcher.current = "view_students"
        elif button_id == "btn_academics":
            switcher.current = "view_academics"
        elif button_id == "btn_reports":
            switcher.current = "view_reports"
        elif button_id == "btn_system":
            self.exit()

if __name__ == "__main__":
    app = EDATuiApp()
    app.run()
