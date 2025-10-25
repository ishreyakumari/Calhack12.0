import os

from llms.groq_llm import GroqLLM
from chains.prompt_generator import PromptGeneratorChain


class DummyLLM(GroqLLM):
    def __init__(self):
        # bypass GroqLLM init
        self.model = "test"

    def generate(self, prompt: str, *args, **kwargs):
        # Return two-line prompt + negative as a single string (two lines)
        return (
            "A cinematic photo of a lone lighthouse on rocky cliffs, dramatic stormy skies, 50mm, shallow depth of field, warm rim lighting, high detail, 8k, photorealistic\nNegative: low-res, watermark, text, logo"
        )


def test_prompt_generator_simple():
    llm = DummyLLM()
    chain = PromptGeneratorChain(llm=llm)
    out = chain.run("a lonely lighthouse at sunset", style="cinematic", aspect="16:9")
    assert "lighthouse" in out["prompt"] or "Lighthouse" in out["prompt"]
