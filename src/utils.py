import pandas as pd
import io

def load_csv(uploaded_file):
    """Safe CSV loader."""
    if uploaded_file is not None:
        try:
            return pd.read_csv(uploaded_file)
        except Exception as e:
            return None
    return None

def convert_df_to_excel(df):
    """Convert dataframe to BytesIO excel file."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    processed_data = output.getvalue()
    return processed_data