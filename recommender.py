import sqlite3
import pandas as pd
import numpy as np
import pickle
from sklearn.metrics.pairwise import cosine_similarity

def generate_nlp_recommendations(target_user):
    # 1. Load pre-computed vector space artifacts from disk
    try:
        with open("tfidf_matrix.pkl", "rb") as f:
            tfidf_matrix = pickle.load(f)
    except FileNotFoundError:
        print("Error: Vector matrix artifacts not found. Run db_manager.py first.")
        return None

    conn = sqlite3.connect('production_movies.db')
    
    # Load all indexed movies to maintain row synchronization with the matrix
    df_all_movies = pd.read_sql_query("SELECT movie_id, title FROM Movies", conn)
    
    # Extract user watch history
    sql_user_history = f'''
    SELECT movie_id FROM Watch_History 
    WHERE user_name = '{target_user}' AND user_rating >= 4.0;
    '''
    df_history = pd.read_sql_query(sql_user_history, conn)
    conn.close()
    
    if df_history.empty:
        return None
        
    favorite_movie_ids = df_history['movie_id'].tolist()

    # 2. Find matching indices between database and matrix rows
    user_fav_indices = df_all_movies[df_all_movies['movie_id'].isin(favorite_movie_ids)].index.tolist()
    
    if not user_fav_indices:
        return None

    # 3. Compute vector mean and apply instant cosine math
    user_text_vector = np.asarray(tfidf_matrix[user_fav_indices].mean(axis=0))
    similarity_scores = cosine_similarity(user_text_vector, tfidf_matrix)

    # 4. Format and sort results
    df_all_movies['Match_Score'] = similarity_scores[0]
    recommendations = df_all_movies[~df_all_movies['movie_id'].isin(favorite_movie_ids)]
    recommendations = recommendations.sort_values(ascending=False, by='Match_Score')
    
    return recommendations[['title', 'Match_Score']]