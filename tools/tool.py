from typing import Any, Dict


class Tool:
    """Base Tool interface."""

    def name(self) -> str:
        raise NotImplementedError()

    def description(self) -> str:
        return "No description provided."

    def run(self, input: str) -> Any:
        raise NotImplementedError()


class EchoTool(Tool):
    def name(self) -> str:
        return "echo"

    def description(self) -> str:
        return "Echoes the input back."

    def run(self, input: str) -> Dict[str, str]:
        return {"output": input}


class CalcTool(Tool):
    def name(self) -> str:
        return "calc"

    def description(self) -> str:
        return "Evaluates a python expression (safe-ish)."

    def run(self, input: str) -> Dict[str, str]:
        # WARNING: eval is dangerous. This is a demo only.
        try:
            result = eval(input, {"__builtins__": {}}, {})
        except Exception as e:
            return {"error": str(e)}
        return {"result": result}
