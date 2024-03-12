import database
import sys
import csv
import mysql.connector

def create_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="NoahHensley",
            password="Redacted",
            database="schema"
        )
        if conn.is_connected():
            return conn
    except Error as e:
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

    for table in table_list:
        query = "DROP TABLE IF EXISTS " + table + " ;"
        cursor.execute(query)
    
    # Create table by running sql file
    sql_file_path = "schema.sql"

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
    # Implement later

    pass


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
