from typing import List

from llms.groq_llm import GroqLLM
from tools.tool import Tool


class BasicAgent:
    """A very small agent that uses an LLM and a set of tools.

    This agent is intentionally simple: it builds a prompt that lists available
    tools and asks the LLM to produce a response. The agent recognizes two
    directives in the LLM's output:
    - ACTION: <tool_name> <json_args>
    - FINAL: <final answer text>
    """

    def __init__(self, llm: GroqLLM, tools: List[Tool]):
        self.llm = llm
        self.tools = {t.name(): t for t in tools}

    def _build_prompt(self, user_input: str) -> str:
        tool_list = "\n".join([f"- {name}: {t.description()}" for name, t in self.tools.items()])
        prompt = f"You are an agent. Available tools:\n{tool_list}\n\nUser: {user_input}\nRespond with either 'ACTION: <tool_name> <arg>' or 'FINAL: <answer>'."
        return prompt

    def run(self, user_input: str) -> str:
        prompt = self._build_prompt(user_input)
        out = self.llm.generate(prompt)

        # Very small parsing logic
        if out.strip().upper().startswith("ACTION:"):
            # Expect format: ACTION: tool_name args...
            try:
                _, rest = out.split(":", 1)
                parts = rest.strip().split(None, 1)
                tool_name = parts[0]
                args = parts[1] if len(parts) > 1 else ""
                tool = self.tools.get(tool_name)
                if not tool:
                    return f"Unknown tool: {tool_name}"
                result = tool.run(args)
                return f"TOOL_RESULT: {result}"
            except Exception as e:
                return f"ERROR parsing action: {e}"

        if out.strip().upper().startswith("FINAL:"):
            return out.split(":", 1)[1].strip()

        # Default: return full LLM text
        return out
