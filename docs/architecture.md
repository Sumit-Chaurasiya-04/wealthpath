# WealthPath Architecture

## Core Components
1.  **Frontend (app.py):** Built with Streamlit. Handles user input, file uploads, and visualization.
2.  **Logic Layer (src/):**
    * `ml_engine.py`: Encapsulates Scikit-Learn pipelines.
    * `database.py`: Abstracts SQLite CRUD operations.
3.  **Data Layer:** Local `wealthpath.db` (SQLite) file.

## Data Flow
1.  CSV -> `pd.read_csv` -> Column Mapping -> `FinanceAI.predict_categories` -> SQLite.
2.  Dashboard -> SQLite Query -> `FinanceAI.forecast_balance` -> Plotly Chart.

## Model Swapping
To swap the Random Forest for a Transformer model (e.g., BERT):
1.  Edit `src/ml_engine.py`.
2.  Replace `TfidfVectorizer` with `HuggingFaceEmbeddings` (requires `sentence-transformers`).
3.  Ensure the input to the classifier is the embedding vector.