import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.pipeline import Pipeline
import joblib
import os

MODEL_PATH = "transaction_classifier.pkl"

class FinanceAI:
    def __init__(self):
        self.category_model = None
        self.vectorizer = None

    def train_categorizer(self, df):
        """
        Train a model to predict categories based on transaction descriptions.
        """
        if df.empty or 'category' not in df.columns:
            return "Not enough data to train."

        # Filter out rows where category is missing
        training_data = df.dropna(subset=['category'])
        
        if len(training_data) < 10:
            return "Need at least 10 categorized transactions to train."

        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(stop_words='english', max_features=500)),
            ('clf', RandomForestClassifier(n_estimators=100, random_state=42))
        ])

        pipeline.fit(training_data['description'], training_data['category'])
        self.category_model = pipeline
        
        # Save model locally
        joblib.dump(self.category_model, MODEL_PATH)
        return "Model trained successfully."

    def predict_categories(self, df):
        """
        Predict categories for transactions with missing categories.
        """
        # Load model if not in memory
        if self.category_model is None:
            if os.path.exists(MODEL_PATH):
                self.category_model = joblib.load(MODEL_PATH)
            else:
                return df # Cannot predict

        # Only predict for rows with missing or 'Misc' category
        mask = (df['category'].isna()) | (df['category'] == '') | (df['category'] == 'Misc')
        
        if mask.sum() > 0:
            descriptions = df.loc[mask, 'description']
            predictions = self.category_model.predict(descriptions)
            df.loc[mask, 'category'] = predictions
            df.loc[mask, 'is_predicted'] = 1
            
        return df

    def forecast_balance(self, df, days_forward=30):
        """
        Predict daily closing balance for the next N days.
        Uses Random Forest Regressor on time features (Day of Year, Day of Week).
        """
        if df.empty:
            return None

        # Prepare daily balance series
        daily = df.groupby('date')['amount'].sum().reset_index()
        daily = daily.sort_values('date')
        
        # Create cumulative balance
        daily['balance'] = daily['amount'].cumsum()
        
        # Feature Engineering
        daily['day_ordinal'] = daily['date'].map(pd.Timestamp.toordinal)
        daily['day_of_week'] = daily['date'].dt.dayofweek
        daily['month'] = daily['date'].dt.month

        X = daily[['day_ordinal', 'day_of_week', 'month']]
        y = daily['balance']

        # Train regressor
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)

        # Create future dates
        last_date = daily['date'].max()
        future_dates = [last_date + pd.Timedelta(days=i) for i in range(1, days_forward + 1)]
        
        future_df = pd.DataFrame({'date': future_dates})
        future_df['day_ordinal'] = future_df['date'].map(pd.Timestamp.toordinal)
        future_df['day_of_week'] = future_df['date'].dt.dayofweek
        future_df['month'] = future_df['date'].dt.month

        # Predict
        future_df['predicted_balance'] = model.predict(future_df[['day_ordinal', 'day_of_week', 'month']])
        
        return future_df[['date', 'predicted_balance']]
    
    def detect_anomalies(self, df):
        """
        Identify transactions that are unusually high for their category.
        """
        anomalies = []
        if df.empty: return anomalies
        
        # Calculate mean and std per category
        stats = df.groupby('category')['amount'].agg(['mean', 'std']).reset_index()
        
        for _, row in df.iterrows():
            cat_stats = stats[stats['category'] == row['category']]
            if not cat_stats.empty:
                mean = cat_stats['mean'].values[0]
                std = cat_stats['std'].values[0]
                
                # Z-score > 2 (Spending only, so look at negative amounts)
                if row['amount'] < 0 and std > 0:
                    z_score = abs(row['amount'] - mean) / std
                    if z_score > 2.5: # 2.5 standard deviations
                        anomalies.append(row)
                        
        return pd.DataFrame(anomalies)