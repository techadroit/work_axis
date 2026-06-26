# PersonalAI

A FastAPI-based AI application with support for multiple LLM providers, RAG (Retrieval-Augmented Generation), vector databases, and secure HTTPS communication.

## Features

✨ **Multi-Provider LLM Support** - OpenAI, Anthropic, Google, AWS Bedrock, Together AI, Ollama
✨ **RAG Pipeline** - Document processing with Docling, vector search with ChromaDB
✨ **SSL/HTTPS Support** - Secure communication with auto-generated certificates
✨ **Executable Builds** - Create standalone applications with PyInstaller
✨ **WebSocket Support** - Real-time streaming responses
✨ **Agent Framework** - LangGraph-based agent orchestration

## Quick Start

### Using Interactive Menu (Recommended)
```bash
./start.sh
```

### Manual Start

**Install uv (one time):**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Install dependencies:**
```bash
uv sync
```

**Run server (HTTP):**
```bash
uv run python backend/run_server.py
# Server available at http://127.0.0.1:8001
```

**Run server (HTTPS with SSL):**
```bash
export ENABLE_SSL=true
uv run python backend/run_server.py
# Server available at https://127.0.0.1:8001
```

## Documentation

- 📖 [Quick Reference](QUICK_REFERENCE.md) - Common commands and tasks
- 📖 [Setup Guide](SETUP_GUIDE.md) - Complete installation and configuration
- 📖 [Build Guide](BUILD_GUIDE.md) - Creating standalone executables
- 📖 [Implementation Summary](IMPLEMENTATION_SUMMARY.md) - Technical details

## SSL/HTTPS Configuration

PersonalAI supports secure HTTPS communication with automatic SSL certificate generation.

**Enable HTTPS:**
```bash
export ENABLE_SSL=true
uv run python backend/run_server.py
```

Self-signed certificates are automatically generated on first run. For production, replace with CA-signed certificates in `data/ssl_certs/`.

See [Setup Guide](SETUP_GUIDE.md) for detailed SSL configuration.

## Building Executable

Create a standalone executable for distribution:

```bash
python build_executable.py
```

The executable will be available in `dist/PersonalAI/` (or `dist/PersonalAI.app` on macOS).

See [Build Guide](BUILD_GUIDE.md) for detailed build instructions.

## Model Download

Download the Mistral model from:
https://huggingface.co/QuantFactory/Mistral-7B-v0.3-GGUF?show_file_info=Mistral-7B-v0.3.Q8_0.gguf

Embedding models are automatically downloaded on first run.

## Environment Variables

Create a `.env` file (copy from `.env.example`):

```bash
# SSL Configuration
ENABLE_SSL=false          # Enable HTTPS server
VERIFY_SSL=true           # Verify SSL for API calls

# API Keys
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here
GOOGLE_API_KEY=your-key-here
```

## Testing

Verify your setup:
```bash
uv run pytest -q
```

## API Documentation

Once running, visit:
- **API Docs:** http://127.0.0.1:8001/docs
- **ReDoc:** http://127.0.0.1:8001/redoc

## Project Structure

```
PersonalAI/
├── server/          # FastAPI application
├── llm/            # LLM provider integrations
├── rag/            # RAG pipeline
├── vector_db/      # Vector database integrations
├── utils/          # Utility modules
├── data/           # Data storage
│   ├── database/   # SQLite database
│   ├── ssl_certs/  # SSL certificates
│   └── vector_database/  # Vector storage
└── docs/           # Documentation
```

## Requirements

- Python 3.12
- uv (https://docs.astral.sh/uv/)
- Dependencies are managed in `pyproject.toml`

## License

[Your License Here]

