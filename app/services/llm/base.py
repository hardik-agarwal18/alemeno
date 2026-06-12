from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseLLMProvider(ABC):
    @abstractmethod
    def categorize_transactions(self, transactions: List[Dict[str, Any]]) -> List[str]:
        """
        Takes a list of transaction dictionaries and returns a list of categories
        (in the same order).
        """
        pass

    @abstractmethod
    def generate_summary(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Takes aggregated job data and returns a dictionary with 'risk_level' and 'narrative'.
        """
        pass
