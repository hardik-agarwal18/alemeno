from app.services.llm.base import BaseLLMProvider
from app.services.llm.gemini import GeminiProvider
from app.services.llm.openai_provider import OpenAIProvider
from app.core.config import settings

def get_llm_provider() -> BaseLLMProvider:
    if settings.LLM_PROVIDER.lower() == "openai":
        return OpenAIProvider()
    elif settings.LLM_PROVIDER.lower() == "gemini":
        return GeminiProvider()
    else:
        return OpenAIProvider()
