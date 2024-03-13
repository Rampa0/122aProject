import mysql.connector


# Replace the following with your MySQL database connection details
config = {
    'user': 'root',
    'password': 'password',
    'host': 'localhost',
    'database': 'main',
}

cnx = mysql.connector.connect(user = 'root', password ='password', database='main')
cursor = cnx.cursor()

# Disable foreign key checks to avoid issues with dependencies
cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

# Retrieve the names of all tables in the database
cursor.execute("SHOW TABLES;")
tables = cursor.fetchall()

# Generate DROP TABLE statements for each table and execute them
for (table_name,) in tables:
    cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`;")
    print(f"Dropped table {table_name}")

# Enable foreign key checks back
cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

# Close the cursor and connection
cursor.close()
cnx.close()