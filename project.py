import database
import sys
import csv
import os
import mysql.connector
from mysql.connector import Error
from constants import Constants
from datetime import datetime


def create_connection():
    conn = None
    try:
        conn = mysql.connector.connect(
            host=Constants.HOSTNAME,
            user=Constants.USERNAME,
            password=Constants.PASSWORD,
            database=Constants.DATABASE
        )
    except Error as e:
        print(f"Error: {e}")
    return conn


# Function to drop tables if they exist and create new ones
def delete_and_create_tables(conn):
    cursor = conn.cursor()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    # List of table names to be dropped
    table_list = [
        "UserEmail",
        "StudentUseMachineInProject",
        "AdministratorManageMachine",
        "Student",
        "Administrator",
        "User",
        "Course",
        "Project",
        "Machine",
    ]
    for table in table_list:
        cursor.execute(f"DROP TABLE IF EXISTS {table};")
        print(f'dropping table {table}')
    print('-----')
    # Assuming 'schema.sql' is in the same directory as 'project.py' --later on we might need to rearange all of the fils into different directory
    with open('schema.sql', 'r') as file:
        sql_script = file.read()
    for statement in sql_script.split(';'):
        if statement.strip():
            cursor.execute(statement)
            print(f'adding {statement}')

    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    conn.commit()
    cursor.close()


def detect_and_format_date(value):
    possible_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']

    for date_format in possible_formats:
        try:
            return datetime.strptime(value, date_format).strftime('%Y-%m-%d')
        except ValueError:
            continue
    return value


def import_csv_data(folder_name):
    conn = create_connection()
    if not conn:
        print("Failed to connect to the database.")
        return

    delete_and_create_tables(conn)
    cursor = conn.cursor()

    files_to_table = [
        ["users", "User"],
        ["emails", "UserEmail"],
        ["students", "Student"],
        ["admins", "Administrator"],
        ["courses", "Course"],
        ["projects", "Project"],
        ["machines", "Machine"],
        ["use", "StudentUseMachineInProject"],
        ["manage", "AdministratorManageMachine"]
    ]

    for file_name, table_name in files_to_table:
        file_path = os.path.join(folder_name, file_name + ".csv")
        with open(file_path, mode='r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if table_name in ["StudentUseMachineInProject"]:
                    row = [detect_and_format_date(value) for value in row]

                placeholders = ', '.join(['%s'] * len(row))
                query = f"INSERT INTO {table_name} VALUES ({placeholders});"
                try:
                    cursor.execute(query, tuple(row))
                except mysql.connector.Error as err:
                    print(f"Error inserting data: {err}")
                    print(f"Query: {query}")
                    print(f"Row: {row}")

    conn.commit()
    cursor.close()
    conn.close()


def insert_student(ucid, email, first, middle, last):
    conn = create_connection()
    try:
        cursor = conn.cursor()

        user_insert_query = """
        INSERT INTO User (UCINetID, name_first, name_middle, name_last)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE UCINetID=UCINetID;
        """
        middle_value = None if middle.upper() == "NULL" else middle
        user_data = (ucid, first, middle_value, last)
        cursor.execute(user_insert_query, user_data)

        student_insert_query = "INSERT INTO Student (UCINetID) VALUES (%s)"
        cursor.execute(student_insert_query, (ucid,))

        email_insert_query = "INSERT INTO UserEmail (UCINetID, Email) VALUES (%s, %s)"
        cursor.execute(email_insert_query, (ucid, email,))

        conn.commit()
        return True
    except Error as e:
        print(f"Error: {e}")
        return False
    finally:
        if conn:
            conn.close()


def add_email_to_user(ucid, email):
    conn = create_connection()
    if conn is None:
        print("Failed to connect to the database.")
        return False

    try:
        cursor = conn.cursor()

        # Check if the UCINetID exists in the User table
        cursor.execute("SELECT COUNT(*) FROM User WHERE UCINetID = %s", (ucid,))
        if cursor.fetchone()[0] == 0:
            print(f"No user found with UCINetID: {ucid}")
            return False

        # Insert the email into the UserEmail table
        insert_query = "INSERT INTO UserEmail (UCINetID, Email) VALUES (%s, %s)"
        cursor.execute(insert_query, (ucid, email))
        conn.commit()
        return True
    except Error as e:
        print(f"Error: {e}")
        return False
    finally:
        if conn:
            conn.close()


def insert_use_record(proj_id, ucinetid, machine_id, start_date, end_date):
    conn = create_connection()
    try:
        cursor = conn.cursor()

        # Check if the student exists
        cursor.execute("SELECT UCINetID FROM Student WHERE UCINetID = %s", (ucinetid,))
        result = cursor.fetchone()

        if result is None:
            print(f"Error: No student found with UCINetID {ucinetid}")
            return False

        # Check if the project exists
        cursor.execute("SELECT project_id FROM Project WHERE project_id = %s", (proj_id,))
        result = cursor.fetchone()

        if result is None:
            print(f"Error: No project found with project_id {proj_id}")
            return False

        # Check if the machine exists
        cursor.execute("SELECT machine_id FROM Machines WHERE machine_id = %s", (machine_id,))
        result = cursor.fetchone()

        if result is None:
            print(f"Error: No machine found with machine_id {machine_id}")
            return False


        # If the student exists, insert the use record
        insert_query = """
        INSERT INTO StudentUseMachineInProject (project_id, UCINetID, machine_id, start_date, end_date)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (proj_id, ucinetid, machine_id, start_date, end_date))
        conn.commit()
        return True
    except Error as e:
        print(f"Error: {e}")
        return False
    finally:
        if conn:
            conn.close()


def update_course(course_id, title):
    conn = create_connection()
    try:
        cursor = conn.cursor()
        # Check if the course exists
        cursor.execute("SELECT title FROM Course WHERE course_id = %s", (course_id,))
        result = cursor.fetchone()

        if result is None:
            print(f"Error: No course found with course_id {course_id}")
            return False
        update_query = "UPDATE Course SET title = %s WHERE course_id = %s"
        cursor.execute(update_query, (title, course_id))
        conn.commit()
        return True
    except Error as e:
        print(f"Error: {e}")
        return False
    finally:
        if conn:
            conn.close()


def main():

    # 1 IMPORT
    if sys.argv[1] == "import" and len(sys.argv) == 3:
        import_csv_data(sys.argv[2])

    # 2 INSERT STUDENT
    elif sys.argv[1] == "insertStudent" and len(sys.argv) == 7:
        result = insert_student(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
        print("Success" if result else "Fail")

    # 3 INSERT EMAIL
    elif sys.argv[1] == "addEmail" and len(sys.argv) == 4:
        result = add_email_to_user(sys.argv[2], sys.argv[3])
        print("Success" if result else "Fail")

    # 6 Insert use record
    elif sys.argv[1] == "insertUse" and len(sys.argv) == 7:
        result = insert_use_record(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
        print("Success" if result else "Fail")

    else:
        print("Invalid arguments")




if __name__ == '__main__':
    main()

