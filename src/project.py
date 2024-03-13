import database
import sys
import csv
import mysql.connector
import constants

def create_connection():
    try:
        conn = mysql.connector.connect(
            host=constants.HOSTNAME,
            user=constants.USERNAME,
            password=constants.PASSWORD,
            database=constants.DATABASE
        )

        if conn.is_connected():
            return conn
        else:
            print("Connection failed!")
    except mysql.connector.Error as e:
        print(e)


def delete_and_create_tables(conn):
    cursor = conn.cursor()
    
    table_list = [
        "User",
        "UserEmail",
        "Student",
        "Administrator",
        "Course",
        "Project",
        "Machine",
        "StudentUseMachineInProject",
        "AdministratorManageMachine"
    ]

    # Going through list reversed to avoid removing
    # tables that other tables depend on through
    # foreign keys
    for table in reversed(table_list):
        query = "DROP TABLE IF EXISTS " + table + ";"
        cursor.execute(query)
    
    # Create table by running sql file
    sql_file_path = "src/schema.sql"

    with open(sql_file_path, 'r') as file:
        sql_script = file.read()

    # Execute each statement in the SQL file
    for statement in sql_script.split(';'):
        # Ignore empty statements (which can occur due to splitting by ';')
        if statement.strip():
            print("running: ", statement)
            cursor.execute(statement)
    
    conn.commit()
    cursor.close()


def import_csv_data(conn):
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

    for file_to_table in files_to_table:
        file_path = "test_data/" + file_to_table[0] + ".csv"
        with open(file_path, mode='r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                query = "INSERT INTO " + file_to_table[1] + " VALUES ("
                for i in range(len(row)):
                    if i != len(row) - 1:
                        query += "\"" + row[i] + "\", "
                    else:
                        query += "\"" + row[i] + "\""
                query += ");"

                cursor.execute(query)
        
    conn.commit()
    cursor.close()


def main():

    conn = create_connection()

    if sys.argv[1] == "import" and len(sys.argv) == 3:
        folder_name = sys.argv[2]
        delete_and_create_tables(conn)
        import_csv_data(conn)
    
    else:
        print("Invalid arguments")


if __name__ == '__main__':
    main()
