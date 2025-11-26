import pandas as pd

def parse_bom(file_path):
    """
    Parses a BOM CSV file, reading only the specified columns for risk analysis.
    """
    try:
        # Add the missing columns here
        df = pd.read_csv(file_path, usecols=['Category', 'HS Code', 'Product Description', 'Company', 'Quantity', 'Net Weight (kg)', 'Total Value (USD)'])
        # Clean up column names by stripping whitespace
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        print(f"Error parsing BOM file: {e}")
        return pd.DataFrame()