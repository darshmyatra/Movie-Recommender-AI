import streamlit as pd
import streamlit as st
import sqlite3
import pandas as pd
from recommender import generate_user_recommendations
from db_manager import initialize_database

# 1. Set up a beautiful page config
st.set_page_config(page_title="AI Movie Recommender", page_icon="🎬", layout="centered")

st.title("🎬 Graduate-Level Movie Recommender AI")
st.write("Welcome to your local vector-space recommendation engine. This system pulls data from a relational SQL database and runs Cosine Similarity algorithms in real-time.")

# Add a handy reset button in case the database needs a refresh
if st.sidebar.button("⚙️ Re-Initialize Database"):
    initialize_database()
    st.sidebar.success("Database refreshed!")

# 2. Dropdown for selecting a User Profile from our database
user_options = ['Darsh', 'Jeet', 'Simoni']
selected_user = st.selectbox("👤 Select a User Profile to analyze:", user_options)

if st.button("🚀 Generate Smart Recommendations"):
    with st.spinner("Calculating vector angles in high-dimensional space..."):
        
        # Call our backend AI module function that we wrote in recommender.py!
        rec_data = generate_user_recommendations(selected_user)
        
        if rec_data is not None and not rec_data.empty:
            st.success(f"Successfully calculated recommendations for {selected_user}!")
            
            # Display the recommendations in a gorgeous formatted interactive table
            st.subheader("🎯 Top Movie Matches for You")
            
            # We filter out match scores of 1.00 because those are movies the user already watched!
            clean_recs = rec_data[rec_data['Match_Score'] < 0.99]
            
            st.dataframe(clean_recs.style.format({"Match_Score": "{:.2f}"}), use_container_width=True)
            
            # Let's add a visual bar chart right inside our app web page!
            st.subheader("📊 Geometric Match Score Breakdown")
            st.bar_chart(data=clean_recs.set_index('title')['Match_Score'])
        else:
            st.error("No watch history found for this user. Click the refresh button in the sidebar to seed data.")