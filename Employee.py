import datetime
import sqlite3

class Employee:
    def __init__(self, employee_id):
        self.employee_id = employee_id

    # Check if the employee ID exists and if the associated user is currently employed
    def check_employee_id(self):
        c.execute("SELECT EmployeeID, Employed FROM Employee WHERE EmployeeID = ?", (self.employee_id,))
        result = c.fetchone()
        if result is None:
            print("Invalid input: Employee ID not found")
            return False
        elif not result[1]:
            print("Invalid input: Associated ID user is not currently employed.")
            return False
        return True

    # Check if the employee is currently clocked in
    def is_clocked_in(self):
        c.execute("SELECT punch_out_time FROM punches WHERE employee_id = ? AND punch_out_time IS NULL", (self.employee_id,))
        result = c.fetchone()
        return result is not None

    def punch(self):
        if not self.check_employee_id():
            return
    
        if self.is_clocked_in():
            # Clock out
            punch_out_time = datetime.datetime.now()
            c.execute("UPDATE punches SET punch_out_time = ? WHERE employee_id = ? AND punch_out_time IS NULL",
                    (punch_out_time, self.employee_id))
            print("Clock out recorded!")
        else:
            # Clock in
            punch_in_time = datetime.datetime.now()
            punch_out_time = None
            c.execute("INSERT INTO punches VALUES (?, ?, ?)", (self.employee_id, punch_in_time, punch_out_time))
            print("Clock in recorded!")
        conn.commit()

# Function to insert new employee data to Employee table
def add_employee(employee_id, first_name, last_name, wage, is_salaried):
    c.execute("INSERT INTO Employee (EmployeeID, Employee_FName, Employee_LName, Wage, IsSalaried, Employed) VALUES (?, ?, ?, ?, ?, ?)",
            (employee_id, first_name, last_name, wage, is_salaried, True))
    conn.commit()

# Function to update the Employed field of the employee to False
def fire(employee_id):
    c.execute("UPDATE Employee SET Employed = ? WHERE EmployeeID = ?", (False, employee_id))
    conn.commit()
    print("Employee with ID {} has been fired.".format(employee_id))

# Prompt for employee number
employee_id = input("Enter your employee number: ")

# Create an instance of an employee
employee = Employee(employee_id)

# Connect to the database
conn = sqlite3.connect('attendance.db')
c = conn.cursor()

# Create the punches table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS punches (
          employee_id INTEGER, 
          punch_in_time TIMESTAMP, 
          punch_out_time TIMESTAMP, 
          FOREIGN KEY (employee_id) REFERENCES Employee(EmployeeID)
          )''')
c.execute('''CREATE TABLE IF NOT EXISTS Employee (
          EmployeeID INTEGER PRIMARY KEY,
          Employee_FName TEXT,
          Employee_LName TEXT,
          Wage FLOAT,
          IsSalaried INTEGER,
          Employed INTEGER
          )''')

# Code used to add sample employee's information to the database
#add_employee(1234567, "John", "Doe", 20.00, False)
#add_employee(7654321, "Jane", "Doe", 27.40, True)

# Code used to test firing sample employee "John Doe"
#fire(1234567)

# Perform punch (clock in or clock out)
employee.punch()

# Close the database connection
conn.close()

