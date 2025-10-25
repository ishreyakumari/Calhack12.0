import os
import sys

# Auto-load a local .env file if present (optional dependency)
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # dotenv is optional; continue if not installed
    pass

from llms.groq_llm import GroqLLM
from agents.basic_agent import BasicAgent
from tools.tool import EchoTool, CalcTool
from chains.prompt_generator import PromptGeneratorChain


def main():
    api_key = os.environ.get("GROQ_API_KEY")
    # Friendly runtime check: report whether the key was loaded (do not print the key)
    if not api_key:
        print("WARNING: GROQ_API_KEY not set. The agent will not be able to call the Groq API.")
        print("Fill the .env file or export GROQ_API_KEY and restart the program.")
    else:
        print("GROQ_API_KEY loaded.")

    model = os.environ.get("GROQ_MODEL", "groq-default")
    api_url = os.environ.get("GROQ_API_URL")

    llm = GroqLLM(model=model, api_key=api_key, api_url=api_url)
    tools = [EchoTool(), CalcTool()]
    agent = BasicAgent(llm=llm, tools=tools)
    prompt_chain = PromptGeneratorChain(llm=llm)

    print("Groq Agent Ready. Modes: [agent] use tool/agent mode, [image] generate image prompt. Type mode, then your input. ('quit' to exit)")
    while True:
        raw = input("> ")
        if raw.strip().lower() in ("quit", "exit"):
            break
        if raw.strip() == "":
            continue
        parts = raw.split(None, 1)
        if len(parts) == 1:
            mode = "agent"
            user = parts[0]
        else:
            mode, user = parts[0], parts[1]

        if mode.lower() == "image":
            # Accept optional style/aspect inline using '::' separator: description :: style :: aspect
            # Example: image a lonely lighthouse at sunset :: cinematic :: 16:9
            segs = [s.strip() for s in user.split("::")]
            description = segs[0]
            style = segs[1] if len(segs) > 1 else None
            aspect = segs[2] if len(segs) > 2 else None
            res = prompt_chain.run(description, style=style, aspect=aspect)
            print("Generated Prompt:")
            print(res["prompt"])
            if res.get("negative"):
                print("Negative Prompt:")
                print(res["negative"])
            continue

        # default to agent
        result = agent.run(user)
        print(result)


if __name__ == "__main__":
    main()
