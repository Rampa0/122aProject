import database
import sys
import csv
import os
import mysql.connector
from mysql.connector import Error
import re
from datetime import datetime


def is_valid_email(email):
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.match(email_regex, email) is not None


def create_connection():
    conn = None
    try:
        from constants import Constants
        conn = mysql.connector.connect(
            host=Constants.HOSTNAME,
            user=Constants.USERNAME,
            password=Constants.PASSWORD,
            database=Constants.DATABASE
        )
    except ModuleNotFoundError:
        conn = mysql.connector.connect(user='test', password='password', database='cs122a')
    except Error as e:
        return None
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
    # Assuming 'schema.sql' is in the same directory as 'project.py' --later on we might need to rearange all of the fils into different directory
    with open('schema.sql', 'r') as file:
        sql_script = file.read()
    for statement in sql_script.split(';'):
        if statement.strip():
            cursor.execute(statement)

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
        return False

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
        try:
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
                        return False
        except:
            return False
    table_names = ["User", "Machine", "Course"]
    row_counts = []
    for table_name in table_names:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        row_count = cursor.fetchone()[0]
        row_counts.append(str(row_count))

    print(",".join(row_counts))

    conn.commit()
    cursor.close()
    conn.close()
    return True


def insert_student(ucid, email, first, middle, last):
    if not is_valid_email(email):
        return False
    conn = create_connection()
    if conn is None:
        return False
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
        return False
    finally:
        if conn:
            conn.close()


def add_email_to_user(ucid, email):
    if not is_valid_email(email):
        return False
    conn = create_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM User WHERE UCINetID = %s", (ucid,))
        if cursor.fetchone()[0] == 0:
            return False

        insert_query = "INSERT INTO UserEmail (UCINetID, Email) VALUES (%s, %s)"
        cursor.execute(insert_query, (ucid, email))
        conn.commit()
        return True
    except Error as e:
        return False
    finally:
        if conn:
            conn.close()


def delete_student(ucid):
    conn = create_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()
        delete_query = "DELETE FROM User WHERE UCINetID = %s"
        cursor.execute(delete_query, (ucid,))
        rows_affected = cursor.rowcount
        conn.commit()
        return rows_affected > 0
    except Error as e:
        return False
    finally:
        if conn:
            conn.close()


def insert_machine(machine_id, hostname, ip_addr, status, location):
    conn = create_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        insert_query = """
        INSERT INTO Machine (machine_id, hostname, IP_address, operational_status, location)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (machine_id, hostname, ip_addr, status, location))
        conn.commit()
        return True
    except Error as e:
        return False
    finally:
        if conn:
            conn.close()



def insert_use_record(proj_id, ucinetid, machine_id, start_date, end_date):

    conn = create_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        if end_date < start_date:
            return False
        # Check if the student exists
        cursor.execute("SELECT UCINetID FROM Student WHERE UCINetID = %s", (ucinetid,))
        result = cursor.fetchone()

        if result is None:
            return False

        # Check if the project exists
        cursor.execute("SELECT project_id FROM Project WHERE project_id = %s", (proj_id,))
        result = cursor.fetchone()

        if result is None:
            return False

        # Check if the machine exists
        cursor.execute("SELECT machine_id FROM Machine WHERE machine_id = %s", (machine_id,))
        result = cursor.fetchone()

        if result is None:
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
        return False
    finally:
        if conn:
            conn.close()


def update_course(course_id, title):
    conn = create_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        # Check if the course exists
        cursor.execute("SELECT title FROM Course WHERE course_id = %s", (course_id,))
        result = cursor.fetchone()

        if result is None:
            return False
        update_query = "UPDATE Course SET title = %s WHERE course_id = %s"
        cursor.execute(update_query, (title, course_id))
        conn.commit()
        return True
    except Error as e:
        return False
    finally:
        if conn:
            conn.close()


def list_course_attended(ucinetid):
    conn = create_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        # Check if the student exists
        cursor.execute("SELECT UCINetID FROM Student WHERE UCINetID = %s", (ucinetid,))
        result = cursor.fetchone()

        if result is None:
            return False

        select_query = """
        SELECT DISTINCT Course.course_id, Course.title, Course.quarter
        FROM Course
        JOIN Project ON Course.course_id = Project.course_id
        JOIN StudentUseMachineInProject ON Project.project_id = StudentUseMachineInProject.project_id
        WHERE StudentUseMachineInProject.UCINetID = %s
        ORDER BY Course.course_id ASC
        """
        cursor.execute(select_query, (ucinetid,))
        rows = cursor.fetchall()
        for row in rows:
            print(','.join(map(str, row)))
        return True
    except Error as e:
        return False
    finally:
        if conn:
            conn.close()


def list_popular_course(n):
    conn = create_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()

        select_query = """
        SELECT Course.course_id, Course.title, COUNT(DISTINCT Student.UCINetID) AS studentCount
        FROM Course
        JOIN Project ON Course.course_id = Project.course_id
        JOIN StudentUseMachineInProject ON Project.project_id = StudentUseMachineInProject.project_id
        JOIN Student ON StudentUseMachineInProject.UCINetID = Student.UCINetID
        GROUP BY Course.course_id, Course.title
        ORDER BY studentCount DESC, Course.course_id DESC
        LIMIT %s;
        """
        cursor.execute(select_query, (n, ))
        rows = cursor.fetchall()
        for row in rows:
            print(','.join(map(str, row)))
        return True
    except Error as e:
        return False
    finally:
        if conn:
            conn.close()


def adminEmails(machine_id):
    conn = create_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        # Check if the student exists
        cursor.execute("SELECT machine_id FROM Machine WHERE machine_id = %s", (machine_id,))
        result = cursor.fetchone()

        if result is None:
            return False

        select_query = """
        SELECT a.UCINetID, u.name_first, u.name_middle, u.name_last, GROUP_CONCAT(e.email SEPARATOR ';')
        FROM Administrator AS a
        JOIN User u ON a.UCINetId = u.UCINetId
        JOIN UserEmail e ON a.UCINetId = e.UCINetId
        JOIN AdministratorManageMachine amm ON amm.UCINetId = a.UCINetId
        WHERE amm.machine_id = %s
        GROUP BY a.UCINetID
        ORDER BY a.UCINetID ASC;
        """
        cursor.execute(select_query, (machine_id,))
        rows = cursor.fetchall()
        for row in rows:
            print(','.join(map(str, row)))
    except Error as e:
        return False
    finally:
        if conn:
            conn.close()


def activeStudent(machineid, n, start, end):
    conn = create_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT machine_id FROM Machine WHERE machine_id = %s", (machineid,))
        result = cursor.fetchone()

        if result is None:
            return False

        select_query = """
        SELECT 
            s.UCINetID, 
            u.name_first, 
            u.name_middle, 
            u.name_last
        FROM 
            StudentUseMachineInProject AS sump
        JOIN 
            Student s ON sump.UCINetID = s.UCINetID
        JOIN 
            User u ON s.UCINetID = u.UCINetID
        WHERE 
            sump.machine_id = %s AND 
            sump.start_date >= %s AND 
            sump.end_date <= %s
        GROUP BY 
            s.UCINetID, u.name_first, u.name_middle, u.name_last
        HAVING 
            COUNT(*) >= %s
        ORDER BY 
            s.UCINetID ASC;
        """
        cursor.execute(select_query, (machineid, start, end, n))
        rows = cursor.fetchall()
        for row in rows:
            print(','.join(map(str, row)))
    except Error as e:
        return False
    finally:
        if conn:
            conn.close()


def machineUsage(courseid):
    conn = create_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        # Check if the student exists
        cursor.execute("SELECT course_id FROM Course WHERE course_id = %s", (courseid,))
        result = cursor.fetchone()

        if result is None:
            return False

        select_query = """
        SELECT 
            m.machine_id, 
            m.hostname, 
            m.IP_address, 
            IFNULL(COUNT(sump.UCINetID), 0) AS count
        FROM 
            Machine m
        LEFT JOIN 
            (SELECT sump.UCINetID, sump.machine_id FROM StudentUseMachineInProject sump 
            JOIN Project p ON sump.project_id = p.project_id 
            WHERE p.course_id = %s) AS sump 
        ON m.machine_id = sump.machine_id
        GROUP BY 
            m.machine_id, m.hostname, m.IP_address
        ORDER BY 
            m.machine_id DESC;
        """
        cursor.execute(select_query, (str(courseid),))
        rows = cursor.fetchall()
        for row in rows:
            print(','.join(map(str, row)))
        return True
    except Error as e:
        print(e)
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

    # 4 DELETE STUDENT
    # THIS ALSO DELETES USER REFERENCES IN USEREMAIL - SHOULD IT?
    # - I think it's okay since USEREMAIL can't do a foreign key reference to a user that doesn't exist
    elif len(sys.argv) == 3 and sys.argv[1] == "deleteStudent":
        result = delete_student(sys.argv[2])
        print("Success" if result else "Fail")

    # 5 INSERT MACHINE
    elif sys.argv[1] == "insertMachine" and len(sys.argv) == 7:
        result = insert_machine(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
        print("Success" if result else "Fail")

    # 6 Insert use record
    elif sys.argv[1] == "insertUse" and len(sys.argv) == 7:
        result = insert_use_record(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
        print("Success" if result else "Fail")

    # 7 Update course
    elif sys.argv[1] == "updateCourse" and len(sys.argv) == 4:
        result = update_course(sys.argv[2], sys.argv[3])
        print("Success" if result else "Fail")

    # 8 Course attended
    elif sys.argv[1] == "listCourse" and len(sys.argv) == 3:
        list_course_attended(sys.argv[2])

    # 9 Popular course
    elif sys.argv[1] == 'popularCourse' and len(sys.argv) == 3:
        list_popular_course(int(sys.argv[2]))

    # 10 Email of admins
    elif sys.argv[1] == 'adminEmails' and len(sys.argv) == 3:
        adminEmails(sys.argv[2])

    # 11 Active students
    elif sys.argv[1] == 'activeStudent' and len(sys.argv) == 6:
        activeStudent(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])

    # 12 Machine usage
    elif sys.argv[1] == 'machineUsage' and len(sys.argv) == 3:
        machineUsage(sys.argv[2])

    else:
        print("Invalid argument")



if __name__ == '__main__':
    main()

