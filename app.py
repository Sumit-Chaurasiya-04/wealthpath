import streamlit as st
import pandas as pd
import plotly.express as px
from src.database import init_db, save_transactions, get_transactions, get_categories, clear_db
from src.ml_engine import FinanceAI
from src.utils import load_csv, convert_df_to_excel

# Initialize
st.set_page_config(page_title="WealthPath", layout="wide")
init_db()
ai = FinanceAI()

# Sidebar
st.sidebar.title("WealthPath")
guided_mode = st.sidebar.toggle("Guided Mode", value=True)
page = st.sidebar.radio("Navigate", ["Dashboard", "Data Import", "Transactions", "Settings"])

if guided_mode:
    st.info("Guided Mode is ON. Look for these blue boxes for explanations of what's happening.")

# --- PAGE: IMPORT ---
if page == "Data Import":
    st.header("Import Bank Data")
    
    if guided_mode:
        st.markdown("""
        **How to use this:**
        1. Download a CSV from your bank website.
        2. Upload it below.
        3. Match your bank's column names to our standard names.
        """)
        
    uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
    
    if uploaded_file:
        df = load_csv(uploaded_file)
        st.write("Preview:", df.head(3))
        
        # Column Mapping
        col1, col2, col3 = st.columns(3)
        with col1:
            date_col = st.selectbox("Which column is Date?", df.columns)
        with col2:
            desc_col = st.selectbox("Which column is Description?", df.columns)
        with col3:
            amt_col = st.selectbox("Which column is Amount?", df.columns)
            
        if st.button("Process & Save"):
            # Standardize
            clean_df = pd.DataFrame({
                'date': pd.to_datetime(df[date_col]),
                'description': df[desc_col],
                'amount': df[amt_col],
                'category': 'Misc', # Default
                'is_predicted': 0
            })
            
            # Auto-Categorize with AI
            if guided_mode:
                st.info("AI is analyzing descriptions to guess categories...")
            
            # Attempt prediction if model exists
            clean_df = ai.predict_categories(clean_df)
            
            save_transactions(clean_df)
            st.success(f"Imported {len(clean_df)} transactions successfully!")

# --- PAGE: DASHBOARD ---
elif page == "Dashboard":
    st.header("Financial Health")
    
    df = get_transactions()
    
    if df.empty:
        st.warning("No data found. Please go to 'Data Import' and upload the sample file.")
    else:
        # KPI Row
        col1, col2, col3 = st.columns(3)
        total_balance = df['amount'].sum()
        monthly_spend = df[df['amount'] < 0]['amount'].sum()
        
        col1.metric("Net Balance", f"${total_balance:,.2f}")
        col2.metric("Total Spending", f"${monthly_spend:,.2f}")
        col3.metric("Transaction Count", len(df))

        # Charts
        c1, c2 = st.columns(2)
        
        # Spending by Category
        spending = df[df['amount'] < 0].groupby('category')['amount'].sum().abs().reset_index()
        fig_pie = px.pie(spending, values='amount', names='category', title="Spending Breakdown")
        c1.plotly_chart(fig_pie, use_container_width=True)
        
        # Balance Over Time
        daily = df.groupby('date')['amount'].sum().cumsum().reset_index()
        fig_line = px.line(daily, x='date', y='amount', title="Balance History")
        c2.plotly_chart(fig_line, use_container_width=True)
        
        # AI Forecast Section
        st.subheader("AI Cash Flow Forecast")
        if guided_mode:
            st.info("This chart uses Machine Learning to look at your history and predict where your balance will be in 30 days.")
            
        if len(df) > 10:
            forecast_df = ai.forecast_balance(df, days_forward=30)
            if forecast_df is not None:
                fig_forecast = px.line(forecast_df, x='date', y='predicted_balance', title="30-Day Wealth Projection")
                # Add dashed line style
                fig_forecast.update_traces(line=dict(dash='dash', color='green'))
                st.plotly_chart(fig_forecast, use_container_width=True)
        else:
            st.warning("Need more data points to generate a reliable forecast.")

        # Anomaly Section
        st.subheader("Detected Anomalies")
        anomalies = ai.detect_anomalies(df)
        if not anomalies.empty:
            st.dataframe(anomalies[['date', 'description', 'amount', 'category']])
        else:
            st.success("No unusual spending detected.")

# --- PAGE: TRANSACTIONS ---
elif page == "Transactions":
    st.header("Transaction Ledger")
    
    df = get_transactions()
    categories = get_categories()
    
    if not df.empty:
        # Editable Data Editor
        edited_df = st.data_editor(
            df,
            column_config={
                "category": st.column_config.SelectboxColumn(
                    "Category",
                    help="Categorize this transaction",
                    width="medium",
                    options=categories,
                    required=True,
                )
            },
            hide_index=True,
        )
        
        if st.button("Save Changes & Train AI"):
            # Clear DB and re-save edited
            clear_db() 
            save_transactions(edited_df)
            
            # Re-train model on new user corrections
            status = ai.train_categorizer(edited_df)
            st.success(f"Saved! {status}")
            
        # Export
        st.divider()
        st.subheader("Export")
        excel_data = convert_df_to_excel(edited_df)
        st.download_button(
            label="Download Excel File",
            data=excel_data,
            file_name="wealthpath_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        if guided_mode:
            st.markdown("Use this Excel file to create Power BI reports.")

# --- PAGE: SETTINGS ---
elif page == "Settings":
    st.header("Settings")
    
    if st.button("Reset Database (Delete All Data)"):
        clear_db()
        st.error("Database cleared.")
        st.rerun()