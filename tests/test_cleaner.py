import os
import pandas as pd
from app.services.transaction_processor.cleaner import DataCleaner

def test_data_cleaner(tmp_path):
    csv_file = tmp_path / "test.csv"
    
    # Create sample CSV with malformed dates, amounts, etc.
    df_raw = pd.DataFrame({
        "txn_id": ["1", "2", "3", "3"], # duplicate txn_id
        "Date": ["2025/05/01", "01-05-2025", "05/01/2025", "05/01/2025"], # mixed dates and duplicate row
        "Merchant ": ["Swiggy", "Zomato", "Uber", "Uber"], # trailing space
        "Amount": ["$1200", "₹500", "1,000", "1,000"],
        " Currency": ["USD", "INR", "INR", "INR"],
        "Status": ["success", "Success", "SUCCESS", "SUCCESS"],
        "Category": ["Food", "", None, None], # missing categories
        "notes": ["Verified", "Duplicate?", None, None]
    })
    
    df_raw.to_csv(csv_file, index=False)
    
    cleaner = DataCleaner(str(csv_file))
    df_clean = cleaner.clean()
    
    # Check deduplication (3 rows remaining)
    assert len(df_clean) == 3
    
    # Check column names lowercased and stripped
    assert list(df_clean.columns) == ["txn_id", "date", "merchant", "amount", "currency", "status", "category", "notes"]
    
    # Check amounts are numeric
    assert df_clean["amount"].tolist() == [1200.0, 500.0, 1000.0]
    
    # Check status is uppercase
    assert all(s == "SUCCESS" for s in df_clean["status"])
    
    # Check category filled
    categories = df_clean["category"].tolist()
    assert categories[0] == "Food"
    assert categories[1] == "Uncategorised"
    assert categories[2] == "Uncategorised"
    
    # Check dates are standardized (YYYY-MM-DD)
    # 2025/05/01 -> 2025-05-01
    # 01-05-2025 -> 2025-05-01 (dayfirst=True)
    dates = df_clean["date"].astype(str).tolist()
    assert dates[0] == "2025-05-01"
    assert dates[1] == "2025-05-01"
    assert dates[2] == "2025-05-01"
