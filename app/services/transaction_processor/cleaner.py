import pandas as pd
import numpy as np
from datetime import datetime

class DataCleaner:
    def __init__(self, filepath: str):
        self.filepath = filepath

    def clean(self) -> pd.DataFrame:
        df = pd.read_csv(self.filepath)
        
        # Lowercase column names and strip whitespace
        df.columns = df.columns.str.lower().str.strip()
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Normalize date
        if 'date' in df.columns:
            # Use format='mixed' and dayfirst=False for ambiguous dates
            df['date'] = pd.to_datetime(df['date'], format='mixed', errors='coerce', dayfirst=True).dt.date
        
        # Normalize amount
        if 'amount' in df.columns:
            df['amount'] = df['amount'].astype(str).str.replace(r'[^\d.-]', '', regex=True)
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            
        # Normalize status
        if 'status' in df.columns:
            df['status'] = df['status'].astype(str).str.upper().str.strip()
            
        # Fill missing categories
        if 'category' in df.columns:
            df['category'] = df['category'].replace({np.nan: None, 'nan': None, '': None})
            df['category'] = df['category'].fillna('Uncategorised')
        else:
            df['category'] = 'Uncategorised'
            
        # Handle malformed rows
        df = df.dropna(subset=['amount', 'date'], how='all')
        
        return df
