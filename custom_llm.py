from typing import Any, List, Optional
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
import requests
import os
from dotenv import load_dotenv

load_dotenv()

class DistilBertLLM(LLM):
    """Custom LLM wrapper for DistilBERT QA model"""
    
    api_url: str = "https://api-inference.huggingface.co/models/distilbert-base-uncased-distilled-squad"
    api_key: str = os.getenv("HUGGINGFACE_API_KEY")

    def _call(
        self, 
        prompt: str, 
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json={
                    "inputs": {
                        "question": prompt,
                        "context": kwargs.get("context", "")
                    }
                }
            )
            response.raise_for_status()
            result = response.json()
            
            # Handle different response formats
            if isinstance(result, list):
                return result[0].get('answer', 'No answer found')
            elif isinstance(result, dict):
                return result.get('answer', 'No answer found')
            return str(result)
        except Exception as e:
            return f"Error: {str(e)}"

    @property
    def _llm_type(self) -> str:
        return "distilbert-qa"