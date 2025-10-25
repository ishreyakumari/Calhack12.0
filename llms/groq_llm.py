import os
import requests
from typing import Optional


class GroqLLM:
    """Minimal Groq LLM wrapper.

    This wrapper is intentionally small and configuration-driven. Some Fetch.ai
    deployment environments require explicit API URL configuration, so the
    endpoint and model are configurable.

    Notes / assumptions:
    - The Groq API endpoint and request shape can vary; this wrapper posts JSON
      to `api_url` with fields `model` and `prompt`. If your Groq API differs,
      set `GROQ_API_URL` to the correct endpoint.
    """

    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None, api_url: Optional[str] = None, timeout: int = 30):
        self.model = model or os.environ.get("GROQ_MODEL", "groq-default")
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        self.api_url = api_url or os.environ.get("GROQ_API_URL", "https://api.groq.ai/v1/completions")
        self.timeout = timeout
        if not self.api_key:
            raise ValueError("GROQ_API_KEY must be set via constructor or GROQ_API_KEY env var")

    def generate(self, prompt: str, max_tokens: int = 256, temperature: float = 0.2) -> str:
        """Generate text synchronously.

        Returns the text output from the LLM. If the service returns structured
        JSON, this method assumes the response contains 'text' or 'choices'.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        try:
            resp = requests.post(self.api_url, json=payload, headers=headers, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            # Network or HTTP error — return a readable error string instead of raising
            # so the agent can handle the failure gracefully.
            return f"LLM_ERROR: {type(e).__name__}: {e}"

        # Try to be flexible about response shape
        if isinstance(data, dict):
            if "text" in data:
                return data["text"]
            if "choices" in data and isinstance(data["choices"], list) and len(data["choices"]) > 0:
                # common shape: {choices: [{text: ...}]}
                first = data["choices"][0]
                if isinstance(first, dict) and "text" in first:
                    return first["text"]
                # sometimes the full text is under 'message'->'content'
                if isinstance(first, dict) and "message" in first and isinstance(first["message"], dict):
                    return first["message"].get("content", "")

        # Fallback: return raw text
        return resp.text


if __name__ == "__main__":
    # Quick manual test harness (will raise if no key)
    llm = GroqLLM()
    out = llm.generate("Say hello in one sentence.")
    print(out)
