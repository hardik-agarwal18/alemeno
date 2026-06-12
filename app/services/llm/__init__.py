from app.services.llm.base import BaseLLMProvider
from app.services.llm.gemini import GeminiProvider
from app.core.config import settings

def get_llm_provider() -> BaseLLMProvider:
    if settings.LLM_PROVIDER.lower() == "gemini":
        return GeminiProvider()
    else:
        # Fallback to Gemini if others not implemented yet
        return GeminiProvider()
