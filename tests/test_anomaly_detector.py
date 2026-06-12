import pandas as pd
from app.services.anomaly_detector.engine import AnomalyDetector

def test_anomaly_detection_amount():
    df = pd.DataFrame({
        "account_id": ["A1", "A1", "A1", "A1"],
        "amount": [100.0, 150.0, 120.0, 1000.0],  # 1000 > 3 * median(120) = 360
        "merchant": ["Shop", "Shop", "Shop", "Shop"],
        "currency": ["USD", "USD", "USD", "USD"]
    })
    
    detector = AnomalyDetector()
    result_df = detector.detect(df)
    
    assert list(result_df["is_anomaly"]) == [False, False, False, True]
    assert "AMOUNT_EXCEEDS_MEDIAN" in result_df.iloc[3]["anomaly_reason"]

def test_anomaly_detection_domestic_usd():
    df = pd.DataFrame({
        "account_id": ["A1", "A2"],
        "amount": [100.0, 150.0],
        "merchant": ["Swiggy", "Zomato"],
        "currency": ["USD", "INR"]
    })
    
    detector = AnomalyDetector()
    result_df = detector.detect(df)
    
    assert list(result_df["is_anomaly"]) == [True, False]
    assert "DOMESTIC_MERCHANT_USD" in result_df.iloc[0]["anomaly_reason"]
    
def test_anomaly_detection_both_rules():
    df = pd.DataFrame({
        "account_id": ["A1", "A1", "A1"],
        "amount": [10.0, 10.0, 100.0], # 100 > 3*10
        "merchant": ["Shop", "Shop", "Uber India"],
        "currency": ["USD", "USD", "USD"]
    })
    
    detector = AnomalyDetector()
    result_df = detector.detect(df)
    
    assert list(result_df["is_anomaly"]) == [False, False, True]
    assert "AMOUNT_EXCEEDS_MEDIAN" in result_df.iloc[2]["anomaly_reason"]
    assert "DOMESTIC_MERCHANT_USD" in result_df.iloc[2]["anomaly_reason"]
