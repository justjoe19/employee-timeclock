# Group 1: Christopher Hochgesang, Tanner Holeton, Joseph Hollenbach and Gheleb Netabai
# SDEV 220 Final Project
# Test
# TODO ADD DESCRIPTION OF WHAT THE PROGRAM DOES
# TODO ADD A MANAGER VIEW THAT MANAGES EMPLOYEE NAMES AND EMPLOYEE NUMBERS IN THE DATABASE

import datetime
import sqlite3


class Employee:
    def __init__(self, employee_id):
        self.employee_id = employee_id

    def is_clocked_in(self):
        c.execute(
            "SELECT punch_type FROM punches WHERE employee_id = ? ORDER BY punch_time DESC LIMIT 1",
            (self.employee_id,),
        )
        result = c.fetchone()
        return result and result[0] == "Clock In"

    def punch(self):
        if self.is_clocked_in():
            punch_type = "Clock Out"
            print("Clock out recorded!")
        else:
            punch_type = "Clock In"
            print("Clock in recorded!")

        current_time = datetime.datetime.now()
        c.execute(
            "INSERT INTO punches VALUES (?, ?, ?)",
            (self.employee_id, current_time, punch_type),
        )
        conn.commit()


# Prompt for employee number
employee_id = input("Enter your employee number: ")

# Create an instance of an employee
employee = Employee(employee_id)

# Connect to the database
conn = sqlite3.connect("attendance.db")
c = conn.cursor()

# Create the punches table if it doesn't exist
c.execute(
    """CREATE TABLE IF NOT EXISTS punches
             (employee_id INTEGER, punch_time TIMESTAMP, punch_type TEXT)"""
)

# Perform punch (clock in or clock out)
employee.punch()

# Close the database connection
conn.close()
