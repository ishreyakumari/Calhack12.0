# Groq Agent (LangChain-like) scaffold

This repository is a minimal LangChain-like scaffold that uses Groq as the LLM backend and is prepared for containerized deployment (e.g., to Fetch.ai). It includes:

- `llms/groq_llm.py`: a small Groq LLM wrapper.
- `agents/basic_agent.py`: a simple agent loop and tool handling.
- `chains/simple_chain.py`: a tiny chain example.
- `tools/tool.py`: Tool base class and examples.
- `examples/run_agent.py`: a runnable demo.
- `tests/test_groq_llm.py`: unit test (mocks the HTTP call).
- `Dockerfile`: container image to run the agent.

Requirements
- Python 3.11+
- `GROQ_API_KEY` environment variable set (or pass via code). Optionally set `GROQ_API_URL` and `GROQ_MODEL`.

Quick start (local)

1. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

2. Export your Groq API key:

```bash
export GROQ_API_KEY="your_key_here"
export GROQ_MODEL="groq-model-v1"
```

3. Run the demo:

```bash
python examples/run_agent.py
```

Run tests:

```bash
pytest -q
```

Docker build & run

Build image:

```bash
docker build -t groq-agent:latest .
```

Run (pass key as env var):

```bash
docker run -e GROQ_API_KEY="$GROQ_API_KEY" groq-agent:latest
```

Notes on Fetch.ai deployment

Fetch.ai supports several hosting/deployment options. This scaffold produces a Docker image which you can adapt to Fetch.ai's hosting or agent runtime. If you'd like, I can add a `deploy/` folder with step-by-step Fetch.ai-specific instructions — tell me which Fetch.ai product you intend to use.
