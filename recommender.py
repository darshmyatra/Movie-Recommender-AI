import sqlite3
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

def generate_user_recommendations(target_user):
    # 1. Open connection to our fresh production database
    conn = sqlite3.connect('production_movies.db')

    # 2. Extract ALL real movies from the database
    df_all_movies = pd.read_sql_query("SELECT * FROM Movies", conn)
    
    # Isolate the mathematical feature columns for our vector space (the binary flags)
    features_all = df_all_movies.set_index('title')[['is_action', 'is_comedy', 'is_scifi']]

    # 3. Extract target user's specific watch history using an INNER JOIN
    sql_user_taste = f'''
    SELECT Movies.is_action, Movies.is_comedy, Movies.is_scifi
    FROM Watch_History
    INNER JOIN Movies ON Watch_History.movie_id = Movies.movie_id
    WHERE Watch_History.user_name = '{target_user}' AND Watch_History.user_rating >= 4.0;
    '''
    df_user_taste = pd.read_sql_query(sql_user_taste, conn)

    # Safety valve: If the user doesn't exist or has no high ratings, exit safely
    if df_user_taste.empty:
        conn.close()
        return None

    # 4. Compute User Taste Vector (Average coordinates of their favorite movie genres)
    user_taste_vector = df_user_taste.mean().values.reshape(1, -1)

    # 5. Execute Cosine Similarity calculations between User Vector and All Movie Vectors
    similarity_scores = cosine_similarity(user_taste_vector, features_all)

    # 6. Map scores back to the movies, sort them, and return the data pipeline results
    df_all_movies['Match_Score'] = similarity_scores[0]
    recommendations = df_all_movies.sort_values(ascending=False, by='Match_Score')
    
    conn.close()
    return recommendations[['title', 'Match_Score']]