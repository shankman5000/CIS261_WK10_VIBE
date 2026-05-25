# William Chris Johnson
# CIS261
# WK10 VIBE Coding

import os
import sys
import termios
import tty

DATA_FILE = "student_grades.txt"

class Student:
    def __init__(self, name: str, student_id: str, test1: float, test2: float, test3: float) -> None:
        self.name = name.strip()
        self.student_id = student_id.strip()
        self.test1 = test1
        self.test2 = test2
        self.test3 = test3
        self.average = self.calculate_average()
        self.grade = self.calculate_grade()

    def calculate_average(self) -> float:
        return round((self.test1 + self.test2 + self.test3) / 3.0, 2)

    def calculate_grade(self) -> str:
        if self.average >= 90:
            return "A"
        if self.average >= 80:
            return "B"
        if self.average >= 70:
            return "C"
        if self.average >= 60:
            return "D"
        return "F"

    def to_line(self) -> str:
        return (
            f"{self.name}|{self.student_id}|{format_score(self.test1)}|"
            f"{format_score(self.test2)}|{format_score(self.test3)}|"
            f"{format_score(self.average)}|{self.grade}"
        )

    @classmethod
    def from_line(cls, line: str):
        parts = [part.strip() for part in line.split("|")]
        if len(parts) != 7:
            raise ValueError("Line does not contain 7 pipe-delimited fields")
        name, student_id, test1, test2, test3, average, grade = parts
        return cls(name, student_id, float(test1), float(test2), float(test3))

    def __str__(self) -> str:
        return (
            f"{self.name:20s} | {self.student_id:10s} | "
            f"{format_score(self.test1):>6s} | {format_score(self.test2):>6s} | "
            f"{format_score(self.test3):>6s} | {format_score(self.average):>6s} | {self.grade}"
        )


def format_score(score: float) -> str:
    return f"{score:.2f}"


def read_single_character() -> str:
    if not sys.stdin.isatty():
        return sys.stdin.read(1)

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def get_menu_choice() -> str:
    print("\nMenu options:")
    print("1 - Add new student")
    print("2 - Display all students")
    print("3 - Display class statistics")
    print("4 - Search student by name")
    print("ESC - Exit and save records")
    print("Choose an option and press Enter, or press ESC:", end=" ")
    sys.stdout.flush()

    choice = read_single_character()
    if choice == "\x1b":
        print("ESC")
        return "ESC"
    print(choice)
    return choice.strip()


def get_nonempty_input(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value.upper() == "ESC":
            raise KeyboardInterrupt
        if value:
            return value
        print("Input cannot be empty. Please try again.")


def get_float_input(prompt: str, min_value: float = 0.0, max_value: float = 100.0) -> float:
    while True:
        value = input(prompt).strip()
        if value.upper() == "ESC":
            raise KeyboardInterrupt
        try:
            score = float(value)
            if score < min_value or score > max_value:
                raise ValueError
            return round(score, 2)
        except ValueError:
            print(f"Invalid score. Enter a number between {min_value} and {max_value}.")


def load_records(filename: str) -> list[Student]:
    students: list[Student] = []
    if not os.path.exists(filename):
        return students

    with open(filename, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                student = Student.from_line(stripped)
                students.append(student)
            except Exception as exc:
                print(f"Warning: could not parse line {line_number}: {exc}")
    return students


def save_records(students: list[Student], filename: str) -> None:
    with open(filename, "w", encoding="utf-8") as file:
        for student in students:
            file.write(student.to_line() + "\n")


def add_student(students: list[Student]) -> None:
    print("\nAdd new student record (type ESC at any prompt to cancel)")
    try:
        name = get_nonempty_input("Student name: ")
        student_id = get_nonempty_input("Student ID: ")
        test1 = get_float_input("Test 1 score: ")
        test2 = get_float_input("Test 2 score: ")
        test3 = get_float_input("Test 3 score: ")
    except KeyboardInterrupt:
        print("\nAdd student canceled.")
        return

    student = Student(name, student_id, test1, test2, test3)
    students.append(student)
    print("Student record added:")
    print(student)


def display_students(students: list[Student]) -> None:
    print("\nStudent Records")
    if not students:
        print("No student records available.")
        return

    print("Name                 | Student ID  |  Test1 |  Test2 |  Test3 | Average | Grade")
    print("----------------------+-------------+--------+--------+--------+---------+-------")
    for student in students:
        print(student)


def display_statistics(students: list[Student]) -> None:
    print("\nClass Statistics")
    if not students:
        print("No student records available.")
        return

    averages = [student.average for student in students]
    highest = max(averages)
    lowest = min(averages)
    class_average = round(sum(averages) / len(averages), 2)
    grade_counts = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    for student in students:
        grade_counts[student.grade] += 1

    print(f"Number of students: {len(students)}")
    print(f"Class average: {format_score(class_average)}")
    print(f"Highest average: {format_score(highest)}")
    print(f"Lowest average: {format_score(lowest)}")
    print("Grade distribution:")
    for letter in ["A", "B", "C", "D", "F"]:
        print(f"  {letter}: {grade_counts[letter]}")


def search_student(students: list[Student]) -> None:
    if not students:
        print("\nNo student records available.")
        return

    query = input("\nEnter student name to search: ").strip().lower()
    if query.upper() == "ESC":
        print("Search canceled.")
        return

    matches = [student for student in students if query in student.name.lower()]
    if not matches:
        print(f"No students found matching '{query}'.")
        return

    print(f"Found {len(matches)} student(s):")
    print("Name                 | Student ID  |  Test1 |  Test2 |  Test3 | Average | Grade")
    print("----------------------+-------------+--------+--------+--------+---------+-------")
    for student in matches:
        print(student)


def main() -> None:
    students = load_records(DATA_FILE)
    print("Student Grade Calculator")
    print("Load complete. Press ESC at the menu to exit and save.")

    while True:
        try:
            choice = get_menu_choice()
            if choice == "ESC":
                break
            if choice == "1":
                add_student(students)
                continue
            if choice == "2":
                display_students(students)
                continue
            if choice == "3":
                display_statistics(students)
                continue
            if choice == "4":
                search_student(students)
                continue

            print("Invalid selection. Choose 1-4 or press ESC.")
        except KeyboardInterrupt:
            print("\nDetected ESC. Exiting...")
            break
        except Exception as exc:
            print(f"An error occurred: {exc}")

    save_records(students, DATA_FILE)
    print(f"Records saved to {DATA_FILE}. Goodbye!")


if __name__ == "__main__":
    main()
