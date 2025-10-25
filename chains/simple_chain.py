from llms.groq_llm import GroqLLM


class SimpleChain:
    """A tiny chain that composes a single LLM call and returns the text."""

    def __init__(self, llm: GroqLLM):
        self.llm = llm

    def run(self, prompt: str) -> str:
        return self.llm.generate(prompt)
