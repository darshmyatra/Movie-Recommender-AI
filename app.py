import streamlit as st
import pandas as pd
from recommender import generate_nlp_recommendations
from db_manager import initialize_database

st.set_page_config(page_title="AI Movie Recommender", page_icon="🎬", layout="centered")

st.title("🎬 Graduate-Level Movie Recommender AI")
st.write("Welcome to your local Natural Language Processing (NLP) engine. This system parses raw English plot summaries using pre-computed TF-IDF vector matrices.")

if st.sidebar.button("⚙️ Re-Initialize Database & Vectors"):
    with st.sidebar.spinner("Building DB and computing embeddings..."):
        initialize_database()
    st.sidebar.success("Database and vectors refreshed!")

user_options = ['Darsh', 'Jeet']
selected_user = st.selectbox("👤 Select a User Profile to analyze:", user_options)

if st.button("🚀 Generate Smart Recommendations"):
    with st.spinner("Executing matrix calculations across 44,000+ records..."):
        
        # Pull raw recommendation array
        rec_data = generate_nlp_recommendations(selected_user)
        
        if rec_data is not None and not rec_data.empty:
            st.success(f"Successfully calculated language-vibe matches for {selected_user}!")
            
            # CRITICAL OPTIMIZATION: Filter out exact history and limit to Top 10 rows for UI rendering
            clean_recs = rec_data[rec_data['Match_Score'] < 0.99].head(10)
            
            st.subheader("🎯 Top 10 Storyline Matches for You")
            st.dataframe(clean_recs.style.format({"Match_Score": "{:.2f}"}), use_container_width=True)
            
            st.subheader("📊 Linguistic Match Score Breakdown")
            st.bar_chart(data=clean_recs.set_index('title')['Match_Score'])
        else:
            st.error("No history found for this user. Please initialize the database.")