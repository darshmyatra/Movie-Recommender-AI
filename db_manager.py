import sqlite3
import pandas as pd
import os
import ast
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer

def clean_genres(genre_string):
    if pd.isna(genre_string):
        return ""
    try:
        genre_list = ast.literal_eval(genre_string)
        return " ".join([genre['name'] for genre in genre_list if 'name' in genre])
    except:
        return ""

def initialize_database():
    db_filename = "production_movies.db"
    
    if os.path.exists(db_filename):
        try:
            os.remove(db_filename)
            print(f"Clean slate activated: Removed old '{db_filename}'")
        except PermissionError:
            print("Warning: Database file is locked.")
            return

    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Movies (
        movie_id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        overview TEXT,
        genres TEXT
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

    print("Reading massive Kaggle CSV metadata...")
    df = pd.read_csv('movies_metadata.csv', low_memory=False)
    df = df.dropna(subset=['id', 'title', 'overview'])
    df['id'] = pd.to_numeric(df['id'], errors='coerce')
    df = df.dropna(subset=['id'])
    df['id'] = df['id'].astype(int)

    print("Parsing unstructured text genres...")
    df['cleaned_genres'] = df['genres'].apply(clean_genres)

    df_movies_to_insert = df[['id', 'title', 'overview', 'cleaned_genres']].drop_duplicates(subset=['id'])
    df_movies_to_insert = df_movies_to_insert.rename(columns={'id': 'movie_id', 'cleaned_genres': 'genres'})

    print(f"Streaming {len(df_movies_to_insert)} movies into SQL storage matrix...")
    df_movies_to_insert.to_sql('Movies', conn, if_exists='append', index=False)

    # Seed watch history
    user_history = [('Darsh', 862, 5.0), ('Darsh', 19995, 4.8), ('Darsh', 155, 4.9), ('Jeet', 12, 5.0)]
    cursor.executemany("INSERT INTO Watch_History (user_name, movie_id, user_rating) VALUES (?, ?, ?)", user_history)
    conn.commit()
    conn.close()

    # ---- NEW PRODUCTION OPTIMIZATION: PRE-COMPUTE VECTORS ----
    print("Pre-computing TF-IDF NLP vectors for all 44,000+ movies...")
    tfidf = TfidfVectorizer(stop_words='english', max_features=5000)
    
    # Generate vectors across the entire dataset once
    tfidf_matrix = tfidf.fit_transform(df_movies_to_insert['overview'])
    
    print("Saving vectorized mathematical artifacts to disk...")
    with open("tfidf_model.pkl", "wb") as f:
        pickle.dump(tfidf, f)
    with open("tfidf_matrix.pkl", "wb") as f:
        pickle.dump(tfidf_matrix, f)
        
    print("Database scale-up and vector pre-computation complete!")

if __name__ == '__main__':
    initialize_database()