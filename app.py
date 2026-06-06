import streamlit as st
import pandas as pd
from recommender import generate_nlp_recommendations
from db_manager import initialize_database

st.set_page_config(page_title="AI Movie Recommender", page_icon="🎬", layout="centered")

st.title("🎬 Graduate-Level Movie Recommender AI")
st.write("Welcome to your local Natural Language Processing (NLP) engine. This system parses raw English plot summaries using TF-IDF text vectorization vectors to match movie vibes.")

if st.sidebar.button("⚙️ Re-Initialize Database"):
    initialize_database()
    st.sidebar.success("Database refreshed!")

user_options = ['Darsh', 'Jeet']
selected_user = st.selectbox("👤 Select a User Profile to analyze:", user_options)

if st.button("🚀 Generate Smart Recommendations"):
    with st.spinner("Analyzing text linguistics and computing matrix cosines..."):
        
        # Call our brand new Phase 4 NLP Text Engine!
        rec_data = generate_nlp_recommendations(selected_user)
        
        if rec_data is not None and not rec_data.empty:
            st.success(f"Successfully calculated language-vibe matches for {selected_user}!")
            
            st.subheader("🎯 Top Storyline Matches for You")
            clean_recs = rec_data[rec_data['Match_Score'] < 0.99]
            
            st.dataframe(clean_recs.style.format({"Match_Score": "{:.2f}"}), use_container_width=True)
            
            st.subheader("📊 Linguistic Match Score Breakdown")
            st.bar_chart(data=clean_recs.set_index('title')['Match_Score'])
        else:
            st.error("No history found for this user.")