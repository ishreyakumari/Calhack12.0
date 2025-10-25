from typing import Optional

from llms.groq_llm import GroqLLM


class PromptGeneratorChain:
    """Generates high-quality image-generation prompts from user descriptions.

    The chain asks the LLM to expand a short description into a detailed image
    prompt including style, camera, lighting, color palette, and negative
    prompts when applicable.
    """

    def __init__(self, llm: GroqLLM):
        self.llm = llm

    def _build_prompt(self, description: str, style: Optional[str] = None, aspect: Optional[str] = None) -> str:
        parts = [
            "You are an expert image prompt engineer.",
            "Given a short user description, produce a single concise, high-quality prompt suitable for image generation models.",
            "Include: subject, environment, lighting, color palette, art style, camera/lens (when relevant), and any important details.",
            "Also include a short `Negative:` section with items the model should avoid (comma-separated).",
            "Output exactly two lines: first line the prompt, second line the negative prompt.",
            "User description: \"" + description + "\"",
        ]

        if style:
            parts.append(f"Prefer style: {style}.")
        if aspect:
            parts.append(f"Target aspect ratio or framing: {aspect}.")

        return "\n".join(parts)

    def run(self, description: str, style: Optional[str] = None, aspect: Optional[str] = None) -> dict:
        prompt = self._build_prompt(description, style=style, aspect=aspect)
        out = self.llm.generate(prompt)

        # Normalize output: accept string, tuple/list, or dict-like response
        if isinstance(out, (list, tuple)):
            out_str = "\n".join([str(o) for o in out])
        elif isinstance(out, dict):
            # attempt to pull text fields
            if "text" in out:
                out_str = str(out["text"])
            elif "choices" in out and isinstance(out["choices"], list) and out["choices"]:
                first = out["choices"][0]
                if isinstance(first, dict):
                    out_str = first.get("text") or first.get("message", {}).get("content", "")
                else:
                    out_str = str(first)
            else:
                out_str = str(out)
        else:
            out_str = str(out)

        # Expecting two lines: prompt and negative
        lines = [l.strip() for l in out_str.splitlines() if l.strip()]
        if len(lines) == 0:
            return {"prompt": "", "negative": ""}

        if len(lines) == 1:
            return {"prompt": lines[0], "negative": ""}

        return {"prompt": lines[0], "negative": lines[1]}
