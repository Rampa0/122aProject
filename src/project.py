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
    # Assuming 'schema.sql' is in the same directory as 'project.py'
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

def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "import":
        import_csv_data(sys.argv[2])
    else:
        print("Invalid arguments")


if __name__ == '__main__':
    main()

