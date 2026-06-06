import sqlite3
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

def generate_user_recommendations(target_user):
    # 1. Connect to the database
    conn = sqlite3.connect('production_movies.db')

    # 2. Extract ALL master movies into a DataFrame
    df_all_movies = pd.read_sql_query("SELECT * FROM Movies", conn)
    features_all = df_all_movies.set_index('title').drop(columns=['movie_id'])

    # 3. Extract target user's history
    sql_user_taste = f'''
    SELECT Movies.action_score, Movies.comedy_score, Movies.scifi_score
    FROM Watch_History
    INNER JOIN Movies ON Watch_History.movie_id = Movies.movie_id
    WHERE Watch_History.user_name = '{target_user}' AND Watch_History.user_rating >= 4.0;
    '''
    df_user_taste = pd.read_sql_query(sql_user_taste, conn)

    if df_user_taste.empty:
        conn.close()
        return None

    # 4. Calculate Taste Vector (The Average)
    user_taste_vector = df_user_taste.mean().values.reshape(1, -1)

    # 5. Vector Matching
    similarity_scores = cosine_similarity(user_taste_vector, features_all)

    # 6. Package and return
    df_all_movies['Match_Score'] = similarity_scores[0]
    recommendations = df_all_movies.sort_values(ascending=False, by='Match_Score')
    
    conn.close()
    return recommendations[['title', 'Match_Score']]