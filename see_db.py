# import sqlite3

# def read_database(db_path):
#     # Connect to the SQLite database
#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()

#     # Example query to fetch all rows from a table called 'users'
#     cursor.execute("SELECT * FROM users")

#     # Fetch all rows
#     rows = cursor.fetchall()

#     # Print out each row
#     for row in rows:
#         print(row)

#     # Close the connection
#     conn.close()

# if __name__ == "__main__":
#     db_path = 'database.db'  # Provide the path to your SQLite database
#     read_database(db_path)
import sqlite3

def read_database(db_path):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query to list all tables (for reference)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in the database:")
    for table in tables:
        print(table[0])

    # Example: Query to select all data from a specific table (replace 'your_table_name')
    table_name = tables[0][0]  # Assuming you want to query the first table found
    print(f"\nData from table '{table_name}':")
    cursor.execute(f"SELECT * FROM {table_name}")

    # Fetch and print all rows
    rows = cursor.fetchall()
    for row in rows:
        print(row)

    # Close the connection
    conn.close()

if __name__ == "__main__":
    db_path = 'database_old.db'  # Provide the path to your SQLite database
    read_database(db_path)

