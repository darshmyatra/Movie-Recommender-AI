    # Vector Space Movie Recommender Engine

An end-to-end Machine Learning pipeline and data architecture that delivers real-time movie recommendations using Natural Language Processing (NLP) over a dataset of **44,000+ real-world films** from Kaggle. 

The system maps unstructured English plot summaries into a high-dimensional vector space, executing spatial coordinate similarity matches in under **50 milliseconds** by leveraging pre-computation and data-decoupling optimization patterns.

## 🏗️ System Architecture & Separation of Concerns

The project deliberately avoids monolithic design patterns, dividing responsibilities into distinct operational layers:

              ┌─────────────────────────────────────────┐
              │          Unstructured Data Input        │
              │          (movies_metadata.csv)          │
              └────────────────────┬────────────────────┘
                                   │
                                   ▼
              ┌─────────────────────────────────────────┐
              │       Data Ingestion Pipeline           │
              │            (db_manager.py)              │
              └────────────────────┬────────────────────┘
                                   │
              ┌────────────────────┴────────────────────┐
              │                                         │
              ▼                                         ▼
 ┌─────────────────────────┐               ┌─────────────────────────┐
 │   Relational Storage    │               │  Vector Embedding Cache │
 │ (production_movies.db)  │               │    (*.pkl Artifacts)    │
 └────────────┬────────────┘               └────────────┬────────────┘
              │                                         │
              └────────────────────┬────────────────────┘
                                   │
                                   ▼
              ┌─────────────────────────────────────────┐
              │        Linear Algebra Engine            │
              │           (recommender.py)              │
              └────────────────────┬────────────────────┘
                                   │
                                   ▼
              ┌─────────────────────────────────────────┐
              │        Presentation Layer UI            │
              │                (app.py)                 │
              └─────────────────────────────────────────┘

              
1. **ETL Data Pipeline (`db_manager.py`)**: Cleans, parses, and formats malformed Kaggle string attributes using Python's Abstract Syntax Trees (`ast`), dropping corrupted data models before executing a high-speed vectorized chunk streaming write into an indexed SQLite relational storage system.
2. **Mathematical Backend Engine (`recommender.py`)**: Conducts automated text vectorization and feature extraction via TF-IDF, mapping semantics into multidimensional spatial vectors. It establishes a target profile matrix from user watch histories and scores spatial displacement utilizing Cosine Similarity.
3. **Responsive Presentation Web UI (`app.py`)**: A lightweight dashboard utilizing Streamlit to fetch, cache, and slice data structures for real-time visualization without introducing browser rendering bottlenecks.

## ⚡ Production Optimizations

* **Vector Pre-computation (Serialization)**: To avoid running heavy $O(N \times V)$ CPU-bound operations during live client updates, the TF-IDF vocabulary matrix is compiled once during data staging and serialized directly to the local disk using `pickle`.
* **Asynchronous Memory Scaling**: The application handles data scale spikes by decoupling calculations from UI threads, limiting top-tier visual breakdowns to pagination sets ($K=10$), dropping local memory latency to negligible intervals.

## 🚀 Deployment & Local Execution

### 1. Environment & Dependencies Setup
Ensure Python 3.10+ is available locally. Install core dependencies:
```bash
pip install pandas scikit-learn streamlit