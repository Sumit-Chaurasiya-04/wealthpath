import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database import get_transactions
import pandas as pd

def main():
    print("Exporting data to Excel...")
    df = get_transactions()
    if df.empty:
        print("No data found in database.")
        return

    output_file = "wealthpath_export.xlsx"
    df.to_excel(output_file, index=False)
    print(f"Success! Data exported to {output_file}")
    print("You can now import this file into Power BI.")

if __name__ == "__main__":
    main()