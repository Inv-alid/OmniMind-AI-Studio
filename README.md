# OmniMind AI Studio

**Ultimate Native Desktop AI Command Center**

Multi-Agent Swarm architecture + Universal LLM Router + RAG + Battle Mode.

Built with **Tauri 2 + React + TypeScript + Tailwind** (frontend) and **Python FastAPI + AsyncIO** (backend).

## Features

- Universal LLM Gateway: OpenAI, Anthropic, Google, xAI (Grok), DeepSeek, Ollama, LM Studio, llama.cpp
- Hierarchical Multi-Agent Swarm (CodeArchitect, Research, DataAnalyst, CreativeVision)
- Model Battle / Consensus Mode
- Local RAG with ChromaDB
- Native desktop performance (Tauri)
- Dark cyberpunk / IDE aesthetic

## Quick Start

### 1. Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
# Fill your API keys in .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8742
```

### 2. Frontend (Tauri)
```bash
npm install
npm run tauri dev
```

### Production Build
```bash
npm run tauri build
```

## Project Structure

```
backend/
  app/
    core/
      router.py          # Universal LLM Router
      agent_swarm.py     # Multi-Agent Orchestrator
      providers/         # All LLM providers
      agents/            # Specialized sub-agents
      rag/               # ChromaDB + Memory
    api/                 # FastAPI routes
src/                     # React + Tauri frontend
src-tauri/               # Tauri configuration
```

## License
MIT
