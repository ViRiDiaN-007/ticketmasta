import sqlite3
import json

def create_sessions_table():
    # Connect to SQLite database
    conn = sqlite3.connect('sessions.db')
    cur = conn.cursor()

    # Create the sessions table if it doesn't exist
    cur.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        otp_link TEXT,
        client_token TEXT,
        cookies TEXT,
        headers TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Commit and close the connection
    conn.commit()
    cur.close()
    conn.close()


def add_account_age_column():
    # Connect to SQLite database
    conn = sqlite3.connect('sessions.db')
    cur = conn.cursor()

    # Add the account_age column if it doesn't exist
    cur.execute('''
    ALTER TABLE sessions ADD COLUMN account_age TEXT
    ''')

    # Commit and close the connection
    conn.commit()
    cur.close()
    conn.close()

# Call this function once to add the column
def update_sessions_table():
    # Connect to SQLite database
    conn = sqlite3.connect('sessions.db')
    cur = conn.cursor()

    # Add the account_age and pw columns if they don't exist
    try:
        cur.execute('''
        ALTER TABLE sessions ADD COLUMN account_age TEXT
        ''')
    except sqlite3.OperationalError:
        # Column already exists
        pass

    try:
        cur.execute('''
        ALTER TABLE sessions ADD COLUMN pw TEXT
        ''')
    except sqlite3.OperationalError:
        # Column already exists
        pass

    # Commit and close the connection
    conn.commit()
    cur.close()
    conn.close()

# Call this function once to update the table
update_sessions_table()