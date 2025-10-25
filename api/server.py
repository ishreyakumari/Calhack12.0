from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

from dotenv import load_dotenv
load_dotenv()

from llms.groq_llm import GroqLLM
from chains.prompt_generator import PromptGeneratorChain
from agents.basic_agent import BasicAgent
from tools.tool import EchoTool, CalcTool


class AgentRequest(BaseModel):
    input: str
    mode: str = "agent"  # or 'image'


class ImageRequest(BaseModel):
    description: str
    style: str | None = None
    aspect: str | None = None


app = FastAPI(title="Groq Agent API")


def _build_runtime():
    api_key = os.environ.get("GROQ_API_KEY")
    model = os.environ.get("GROQ_MODEL", "groq-default")
    api_url = os.environ.get("GROQ_API_URL")
    llm = GroqLLM(model=model, api_key=api_key, api_url=api_url)
    prompt_chain = PromptGeneratorChain(llm=llm)
    tools = [EchoTool(), CalcTool()]
    agent = BasicAgent(llm=llm, tools=tools)
    return llm, prompt_chain, agent


LLM, PROMPT_CHAIN, AGENT = _build_runtime()


@app.post("/image")
def generate_image_prompt(req: ImageRequest):
    """Return a generated image prompt and negative prompt."""
    try:
        out = PROMPT_CHAIN.run(req.description, style=req.style, aspect=req.aspect)
        return {"prompt": out.get("prompt", ""), "negative": out.get("negative", "")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent")
def run_agent(req: AgentRequest):
    """Run the agent in 'agent' or 'image' mode. For image mode returns prompt; for agent mode returns the agent output."""
    mode = req.mode.lower()
    if mode == "image":
        # fallback to prompt generator
        res = PROMPT_CHAIN.run(req.input)
        return {"mode": "image", "prompt": res.get("prompt"), "negative": res.get("negative")}

    if mode == "agent":
        out = AGENT.run(req.input)
        # If the LLM returned an LLM_ERROR string, map to 502
        if isinstance(out, str) and out.startswith("LLM_ERROR:"):
            raise HTTPException(status_code=502, detail=out)
        return {"mode": "agent", "output": out}

    raise HTTPException(status_code=400, detail="unknown mode")


@app.get("/health")
def health():
    return {"status": "ok"}
