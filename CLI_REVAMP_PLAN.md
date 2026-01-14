# CLI Revamp Plan: Interactive Menu System

## Objective
Convert the current CLI to a menu-driven interface.

## Proposed Code Structure

### 1. Main Loop (`src/cli.py`)
- Replace `argparse` with a `while True` loop.
- Display a main menu with numbered options.

### 2. Input Handling
- Implement a helper `get_input(prompt, exit_keyword='q')`.
- Allow users to type 'q' to return to the main menu at any prompt.

### 3. Workflows
- **Add Student**: Interactive prompts for Name, Email, DOB, etc.
- **Enroll**: Prompts for Email, Course, Date.
- **Grade**: Prompts for Email, Course, Type, Score.
- **Attendance**: Prompts for Email, Course, Status.
- **Reports**: Sub-menu for report type and format.

## Example Flow
```text
1. Add Student
2. Exit
Choice: 1
First Name (q to cancel): John
...
```
