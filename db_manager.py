import sqlite3
import pandas as pd
import os

def initialize_database():
    db_filename = "production_movies.db"
    
    # YOUR UPGRADE: Wipe the old database file if it exists to ensure a clean slate
    if os.path.exists(db_filename):
        try:
            os.remove(db_filename)
            print(f"Existing database file '{db_filename}' successfully removed.")
        except PermissionError:
            print(f"Warning: Could not delete '{db_filename}' because it's currently open by another script.")

    # 1. Open a fresh live connection (SQLite will create a brand new file here)
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()

    # 2. Enable Foreign Key constraints
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 3. Create the Movies Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Movies (
        movie_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        action_score REAL,
        comedy_score REAL,
        scifi_score REAL
    )
    ''')

    # 4. Create the Watch_History Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Watch_History (
        history_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT NOT NULL,
        movie_id INTEGER,
        user_rating REAL,
        FOREIGN KEY (movie_id) REFERENCES Movies(movie_id)
    )
    ''')

    # 5. Insert Data into Movies Table
    movies_to_insert = [
        ('Die Hard', 5.0, 1.0, 0.0),
        ('John Wick', 5.0, 0.2, 0.0),
        ('The Hangover', 0.5, 5.0, 0.0),
        ('Superbad', 1.0, 5.0, 0.5),
        ('Avatar', 4.5, 1.0, 5.0)
    ]
    cursor.executemany("INSERT INTO Movies (title, action_score, comedy_score, scifi_score) VALUES (?, ?, ?, ?)", movies_to_insert)

    # 6. Insert Data into Watch_History
    user_history_to_insert = [
        ('Darsh', 1, 4.8),  
        ('Darsh', 2, 4.5),  
        ('Jeet', 3, 5.0)    
    ]
    cursor.executemany("INSERT INTO Watch_History (user_name, movie_id, user_rating) VALUES (?, ?, ?)", user_history_to_insert)
    
    conn.commit()
    conn.close()
    print("Database built and populated successfully from a clean slate!")

if __name__ == '__main__':
    initialize_database()