# create_database.py
import sqlite3

DATABASE = 'database.db'



def create_database():
    """Create a new SQLite database and the users table."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        submitted INTEGER DEFAULT 0
    )
    ''')
    
    
    # Optionally, you can insert test data here
    # cursor.execute("INSERT INTO users (email, password, submitted) VALUES ('test@example.com', 'password123', 0)")

    conn.commit()
    conn.close()
    print(f"Database {DATABASE} created successfully.")

if __name__ == "__main__":
    create_database()

