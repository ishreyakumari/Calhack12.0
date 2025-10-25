# cURL examples for Groq Agent API

This document contains ready-to-copy cURL commands for the FastAPI agent in this repo. Share these with your workflow owners — replace HOST/PORT and headers as needed.

Base: http://127.0.0.1:8000 (change to your deployed host)

## Health check

```bash
curl -s http://127.0.0.1:8000/health | jq .
# => { "status": "ok" }
```

## Generate an image prompt (POST /image)

Request body: {"description": "...", "style": "...", "aspect": "..."}

```bash
curl -s -X POST "http://127.0.0.1:8000/image" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "a lonely lighthouse at sunset",
    "style": "cinematic",
    "aspect": "16:9"
  }' | jq .
```

## Run the agent (agent mode)

```bash
curl -s -X POST "http://127.0.0.1:8000/agent" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Write a 30-second ad script for EcoSip, tone: energetic",
    "mode": "agent"
  }' | jq .
```

## Run the agent (image mode)

```bash
curl -s -X POST "http://127.0.0.1:8000/agent" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "a lonely lighthouse at sunset",
    "mode": "image"
  }' | jq .
```

## Save the generated prompt into a shell variable (useful in CI/workflows)

```bash
PROMPT=$(curl -s -X POST "http://127.0.0.1:8000/image" \
  -H "Content-Type: application/json" \
  -d '{"description":"a cozy cabin in snowy woods at dusk","style":"storybook","aspect":"4:5"}' \
  | jq -r '.prompt')
echo "$PROMPT"
```

## Using an Authorization header (if you add auth)

```bash
curl -s -X POST "http://127.0.0.1:8000/image" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $AGENT_API_TOKEN" \
  -d '{"description":"a futuristic city skyline","style":"sci-fi","aspect":"16:9"}' | jq .
```

## Using a simple API key header (if you add X-API-Key enforcement)

```bash
curl -s -X POST "http://127.0.0.1:8000/agent" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $AGENT_API_KEY" \
  -d '{"input":"a lonely lighthouse at sunset","mode":"image"}' | jq .
```

## Docker (build & run the API container)

Build image:

```bash
docker build -t groq-agent:latest .
```

Run (pass GROQ_API_KEY; exposes port 8000):

```bash
docker run -it --rm -e GROQ_API_KEY="$GROQ_API_KEY" -p 8000:8000 groq-agent:latest \
  uvicorn api.server:app --host 0.0.0.0 --port 8000
```

Then use the same cURL commands against http://localhost:8000

## GitHub Actions snippet (example)

```yaml
- name: Generate image prompt from agent
  env:
    API_URL: ${{ secrets.AGENT_URL }}  # e.g. https://agent.example.com
  run: |
    response=$(curl -s -X POST "${API_URL}/image" \
      -H "Content-Type: application/json" \
      -d '{"description":"a cozy cabin in snowy woods at dusk","style":"storybook","aspect":"4:5"}')
    echo "Prompt response: $response"
```

## Error handling notes

- 200 OK: successful prompt or agent output
- 400 Bad Request: unknown mode or bad payload
- 502 Bad Gateway: LLM/network error (body will contain "LLM_ERROR: ...")
- 500 Internal Server Error: unexpected error

## Security notes

- Keep `GROQ_API_KEY` and any `AGENT_API_KEY` secret. Use environment variables or secret stores in CI.
- Add HTTPS and authentication before exposing the API publicly.
