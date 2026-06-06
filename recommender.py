import sqlite3
import pandas as pd
import numpy as np  # ADDED: Essential for array data type casting
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def generate_nlp_recommendations(target_user):
    # 1. Connect to our database and pull the raw movie entries
    conn = sqlite3.connect('production_movies.db')
    df_movies = pd.read_sql_query("SELECT movie_id, title FROM Movies", conn)
    
    # Read the text descriptions directly from our local CSV data file
    df_csv = pd.read_csv('movies_metadata.csv').dropna(subset=['id', 'title', 'overview'])
    df_csv['id'] = df_csv['id'].astype(int)
    
    # Merge datasets on the unique ID keys
    df_merged = pd.merge(df_movies, df_csv, left_on='movie_id', right_on='id', how='inner')

    # 2. THE NLP ENGINE: Initialize the TF-IDF Vectorizer
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df_merged['overview'])

    # 3. Pull the target user's favorite movie histories
    sql_user_history = f'''
    SELECT movie_id FROM Watch_History 
    WHERE user_name = '{target_user}' AND user_rating >= 4.0;
    '''
    df_history = pd.read_sql_query(sql_user_history, conn)
    conn.close()

    if df_history.empty:
        return None

    # Find the row indices of the movies the user loved
    favorite_movie_ids = df_history['movie_id'].tolist()
    user_fav_indices = df_merged[df_merged['movie_id'].isin(favorite_movie_ids)].index

    # 4. VECTOR MATH: Calculate average Text Vector and force convert to numpy array
    # FIX: Wrapped the expression with np.asarray() to resolve the scikit-learn compatibility issue
    user_text_vector = np.asarray(tfidf_matrix[user_fav_indices].mean(axis=0))

    # 5. MATRIX MATCHING: Compare user's text taste profile against all movie overviews
    similarity_scores = cosine_similarity(user_text_vector, tfidf_matrix)

    # 6. Package and sort results
    df_merged['Match_Score'] = similarity_scores[0]
    recommendations = df_merged.sort_values(ascending=False, by='Match_Score')
    
    return recommendations[['title_x', 'Match_Score']].rename(columns={'title_x': 'title'})