import pandas as pd

class AnomalyDetector:
    DOMESTIC_MERCHANTS = ["Swiggy", "Zomato", "IRCTC", "Ola", "Uber India"]

    def detect(self, df: pd.DataFrame) -> pd.DataFrame:
        df['is_anomaly'] = False
        df['anomaly_reason'] = None
        
        if df.empty:
            return df
            
        # Calculate median per account_id
        if 'account_id' in df.columns and 'amount' in df.columns:
            medians = df.groupby('account_id')['amount'].transform('median')
            
            # Rule 1: amount > 3 * median
            mask_rule1 = (df['amount'] > 3 * medians) & (medians > 0)
            
            # Use loc to set values
            df.loc[mask_rule1, 'is_anomaly'] = True
            
            # For setting the reason, concatenate with existing reason or set it
            reasons = df.loc[mask_rule1, 'anomaly_reason']
            df.loc[mask_rule1, 'anomaly_reason'] = reasons.apply(
                lambda x: "AMOUNT_EXCEEDS_MEDIAN" if pd.isna(x) else x + ", AMOUNT_EXCEEDS_MEDIAN"
            )
            
        # Rule 2: Domestic merchants with USD
        if 'merchant' in df.columns and 'currency' in df.columns:
            # Case insensitive match for domestic merchants
            mask_rule2 = df['merchant'].str.contains('|'.join(self.DOMESTIC_MERCHANTS), case=False, na=False) & (df['currency'].str.upper() == 'USD')
            
            df.loc[mask_rule2, 'is_anomaly'] = True
            reasons = df.loc[mask_rule2, 'anomaly_reason']
            df.loc[mask_rule2, 'anomaly_reason'] = reasons.apply(
                lambda x: "DOMESTIC_MERCHANT_USD" if pd.isna(x) else x + ", DOMESTIC_MERCHANT_USD"
            )
            
        return df
