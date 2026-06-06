import sqlite3
import pandas as pd
import os
import ast

def clean_genres(genre_string):
    """Safely extracts genre names from the messy string format."""
    try:
        # Convert string representation of list into an actual Python list of dictionaries
        genre_list = ast.literal_eval(genre_string)
        # Extract just the 'name' value from each dictionary
        names = [genre['name'] for genre in genre_list]
        return names
    except:
        return []

def initialize_database():
    db_filename = "production_movies.db"
    
    # 1. Wipe old database to ensure a clean slate
    if os.path.exists(db_filename):
        try:
            os.remove(db_filename)
            print(f"Clean slate activated: Removed old '{db_filename}'")
        except PermissionError:
            print("Warning: Database file is currently locked.")

    # 2. Re-create database and tables
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Movies (
        movie_id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        is_action INTEGER DEFAULT 0,
        is_comedy INTEGER DEFAULT 0,
        is_scifi INTEGER DEFAULT 0
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Watch_History (
        history_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT NOT NULL,
        movie_id INTEGER,
        user_rating REAL,
        FOREIGN KEY (movie_id) REFERENCES Movies(movie_id)
    )
    ''')

    # 3. PIPELINE: Load and Clean the CSV data
    print("Loading raw CSV metadata into pipeline...")
    df_raw = pd.read_csv('movies_metadata.csv')

    # Drop rows where crucial details like ID or Title are missing completely
    df_clean = df_raw.dropna(subset=['id', 'title']).copy()

    # Process each row and insert it into the database
    movies_processed = 0
    for _, row in df_clean.iterrows():
        try:
            m_id = int(row['id'])
            title = row['title']
            genres = clean_genres(row['genres'])
            
            # Map genres to binary flags (1 if present, 0 if not)
            is_action = 1 if 'Action' in genres else 0
            is_comedy = 1 if 'Comedy' in genres else 0
            is_scifi = 1 if 'Science Fiction' in genres else 0
            
            cursor.execute('''
                INSERT OR IGNORE INTO Movies (movie_id, title, is_action, is_comedy, is_scifi)
                VALUES (?, ?, ?, ?, ?)
            ''', (m_id, title, is_action, is_comedy, is_scifi))
            movies_processed += 1
        except Exception as e:
            # Skip corrupted rows silently
            continue

    # 4. Seed user history with real movie IDs now
    # User 'Darsh' watched Toy Story (862) and Avatar (19995)
    user_history = [
        ('Darsh', 862, 4.9),  
        ('Darsh', 19995, 4.5),  
        ('Jeet', 12, 5.0)    
    ]
    cursor.executemany("INSERT INTO Watch_History (user_name, movie_id, user_rating) VALUES (?, ?, ?)", user_history)
    
    conn.commit()
    conn.close()
    print(f"Pipeline complete! Successfully parsed and loaded {movies_processed} real movies into the database.")

if __name__ == '__main__':
    initialize_database()