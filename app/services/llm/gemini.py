import json
import time
import logging
from typing import List, Dict, Any
from google import genai
from google.genai import types
from app.core.config import settings
from app.services.llm.base import BaseLLMProvider

logger = logging.getLogger(__name__)

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        import numpy as np
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

class GeminiProvider(BaseLLMProvider):
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if not self.api_key:
            logger.warning("GEMINI_API_KEY is not set. LLM calls will fail.")
        self.client = genai.Client(api_key=self.api_key)
        self.model = 'gemini-1.5-flash'
        
        self.categories = [
            "Food", "Shopping", "Travel", "Transport", 
            "Utilities", "Entertainment", "Healthcare", 
            "Cash Withdrawal", "Other"
        ]

    def _call_with_retry(self, func, *args, **kwargs):
        """Exponential backoff retry: 1s, 2s, 4s"""
        retries = [1, 2, 4]
        for i, wait_time in enumerate(retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"LLM call failed (attempt {i+1}): {str(e)}")
                if i == len(retries) - 1:
                    raise e
                time.sleep(wait_time)
        return None

    def categorize_transactions(self, transactions: List[Dict[str, Any]]) -> List[str]:
        if not transactions:
            return []
            
        prompt = f"""
        Classify the following transactions into exactly ONE of these categories:
        {", ".join(self.categories)}
        
        Transactions (JSON format):
        {json.dumps(transactions, cls=NumpyEncoder)}
        
        Return a JSON list of strings, containing ONLY the category name for each transaction in the exact same order.
        Do not include any markdown formatting, markdown code blocks, or extra text. Just the JSON array.
        """
        
        def _make_call():
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            text = response.text.strip()
            # Handle potential markdown code blocks
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            
            categories = json.loads(text.strip())
            
            # Validate output
            validated = []
            for cat in categories:
                if cat in self.categories:
                    validated.append(cat)
                else:
                    validated.append("Other")
                    
            if len(validated) != len(transactions):
                logger.error(f"LLM returned {len(validated)} categories for {len(transactions)} transactions")
                # Pad with 'Other' if short, truncate if long
                while len(validated) < len(transactions):
                    validated.append("Other")
                validated = validated[:len(transactions)]
                
            return validated
            
        try:
            return self._call_with_retry(_make_call)
        except Exception as e:
            logger.error(f"Final failure in LLM categorization: {str(e)}")
            return ["Other"] * len(transactions)

    def generate_summary(self, data: Dict[str, Any]) -> Dict[str, str]:
        prompt = f"""
        Analyze the following transaction data and generate a summary.
        
        Data:
        {json.dumps(data, cls=NumpyEncoder)}
        
        Provide your response in JSON format exactly like this:
        {{
            "risk_level": "LOW", # or MEDIUM, HIGH
            "narrative": "A short 2-3 sentence paragraph describing the spending patterns and highlighting any risks."
        }}
        
        Return ONLY valid JSON.
        """
        
        def _make_call():
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            text = response.text.strip()
            # Handle potential markdown code blocks
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
                
            result = json.loads(text.strip())
            risk_level = result.get("risk_level", "MEDIUM")
            if risk_level not in ["LOW", "MEDIUM", "HIGH"]:
                risk_level = "MEDIUM"
                
            return {
                "risk_level": risk_level,
                "narrative": result.get("narrative", "Unable to generate narrative.")
            }
            
        try:
            return self._call_with_retry(_make_call)
        except Exception as e:
            logger.error(f"Final failure in LLM summary generation: {str(e)}")
            return {
                "risk_level": "UNKNOWN",
                "narrative": "Failed to generate summary due to LLM error."
            }
