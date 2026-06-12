import pandas as pd
from typing import Dict, Any, List
from app.services.llm import get_llm_provider

class SummaryGenerator:
    def __init__(self):
        self.llm_provider = get_llm_provider()

    def generate(self, df: pd.DataFrame, row_count_clean: int, anomaly_count: int) -> Dict[str, Any]:
        if df.empty:
            return {
                "total_spend_inr": 0.0,
                "total_spend_usd": 0.0,
                "top_merchants": {},
                "anomaly_count": 0,
                "risk_level": "LOW",
                "narrative": "No transactions to summarize."
            }

        # Calculate totals
        spend_inr = df[df['currency'].str.upper() == 'INR']['amount'].sum() if 'currency' in df.columns else 0
        spend_usd = df[df['currency'].str.upper() == 'USD']['amount'].sum() if 'currency' in df.columns else 0

        # Top merchants by amount
        top_merchants_dict = {}
        if 'merchant' in df.columns and 'amount' in df.columns:
            top_merchants_df = df.groupby('merchant')['amount'].sum().sort_values(ascending=False).head(3)
            top_merchants_dict = {k: float(v) for k, v in top_merchants_df.to_dict().items()}

        # Spend by category
        spend_by_category = {}
        if 'category' in df.columns and 'amount' in df.columns:
            spend_by_category = {k: float(v) for k, v in df.groupby('category')['amount'].sum().to_dict().items()}

        # Prepare payload for LLM
        llm_payload = {
            "top_merchants": top_merchants_dict,
            "spend_by_category": spend_by_category,
            "spend_by_currency": {"INR": float(spend_inr), "USD": float(spend_usd)},
            "anomaly_count": int(anomaly_count),
            "transaction_count": int(row_count_clean)
        }

        # Call LLM
        llm_summary = self.llm_provider.generate_summary(llm_payload)

        return {
            "total_spend_inr": float(spend_inr),
            "total_spend_usd": float(spend_usd),
            "top_merchants": top_merchants_dict,
            "spend_by_category": spend_by_category,
            "anomaly_count": anomaly_count,
            "risk_level": llm_summary.get("risk_level", "UNKNOWN"),
            "narrative": llm_summary.get("narrative", "")
        }
