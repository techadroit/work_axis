# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for PersonalAI
Builds a standalone executable bundling the FastAPI/uvicorn server,
LLM integrations, RAG pipeline, ChromaDB, docling, and all supporting modules.
"""

import sys
import os
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules, collect_data_files, copy_metadata

# ── Project root ─────────────────────────────────────────────────────────────
ROOT = os.path.abspath(SPECPATH)   # directory that contains this .spec file

# ── Additional hook search path ───────────────────────────────────────────────
additional_hooks_dir = [os.path.join(ROOT, 'hooks')]

# =============================================================================
# Hidden imports
# =============================================================================
hidden_imports = [
    # ── Standard library extras ───────────────────────────────────────────��──
    'multiprocessing',
    'multiprocessing.freeze_support',
    'asyncio',
    'email.mime.text',
    'email.mime.multipart',

    # ── FastAPI / Uvicorn / Starlette ────────────────────────────────────────
    'fastapi',
    'fastapi.middleware.cors',
    'uvicorn',
    'uvicorn.main',
    'uvicorn.config',
    'uvicorn.server',
    'uvicorn.lifespan.on',
    'uvicorn.protocols.http.h11_impl',
    'uvicorn.protocols.http.httptools_impl',
    'uvicorn.protocols.websockets.websockets_impl',
    'uvicorn.protocols.websockets.wsproto_impl',
    'uvicorn.loops.asyncio',
    'uvicorn.loops.uvloop',
    'uvicorn.logging',
    'starlette',
    'starlette.routing',
    'starlette.middleware.cors',
    'starlette.responses',
    'starlette.websockets',
    'websockets',
    'h11',
    'httptools',
    'python_multipart',

    # ── Pydantic ─────────────────────────────────────────────────────────────
    'pydantic',
    'pydantic.v1',
    'pydantic_core',
    'pydantic[email]',
    'email_validator',

    # ── LangChain & LangGraph ─────────────────────────────────────────────────
    'langchain',
    'langchain_core',
    'langchain_text_splitters',
    'langchain_community',
    'langchain_aws',
    'langchain_openai',
    'langchain_anthropic',
    'langchain_together',
    'langchain_ollama',
    'langchain_google_genai',
    'langchain_mcp_adapters',
    'langgraph',
    'langgraph.checkpoint',
    'langgraph.checkpoint.sqlite',
    'langgraph_checkpoint_sqlite',
    'aiosqlite',

    # ── ChromaDB ─────────────────────────────────────────────────────────────
    'chromadb',
    'chromadb.api',
    'chromadb.api.client',
    'chromadb.api.models',
    'chromadb.config',
    'chromadb.db',
    'chromadb.db.impl',
    'chromadb.db.impl.sqlite',
    'chromadb.segment',
    'chromadb.segment.impl',
    'chromadb.segment.impl.manager',
    'chromadb.segment.impl.metadata',
    'chromadb.segment.impl.vector',
    'chromadb.telemetry',
    'chromadb.telemetry.product',
    'chromadb.telemetry.product.posthog',
    'chromadb.telemetry.events',

    # ── Sentence Transformers / Embeddings ────────────────��───────────────────
    'sentence_transformers',
    'transformers',
    'tokenizers',
    'huggingface_hub',
    'fastembed',

    # ── Docling ───────────────────────────────────���────────────────────��──────
    'docling',
    'docling_core',

    # ── DuckDB / DuckDuckGo ───────────────────────────────────────────────────
    'duckdb',
    'ddgs',
    'ddgs.ddgs',
    'ddgs.exceptions',
    'ddgs.utils',
    'ddgs.base',
    'ddgs.http_client',
    'ddgs.results',
    'ddgs.similarity',
    'ddgs.engines',
    'ddgs.engines.duckduckgo',
    'ddgs.engines.google',
    'ddgs.engines.bing',
    'ddgs.engines.yahoo',
    'ddgs.engines.yandex',
    'ddgs.engines.brave',
    'ddgs.engines.mojeek',
    'ddgs.engines.wikipedia',
    'ddgs.engines.duckduckgo_images',
    'ddgs.engines.duckduckgo_news',
    'ddgs.engines.duckduckgo_videos',
    'primp',

    # ── HTTP / Networking ─────────────────────────────────────────────────────
    'httpx',
    'requests',
    'certifi',
    'urllib3',

    # ── Cryptography / SSL ────────────────────────────────────────────────────
    'cryptography',
    'cryptography.hazmat.primitives',
    'cryptography.hazmat.backends',
    'cryptography.x509',
    'ssl',

    # ── Data / parsing ────────────────────────────────────────────────────────
    'beautifulsoup4',
    'bs4',
    'lxml',
    'lxml.etree',
    'lxml._elementpath',

    # ── Logging / Env ─────────────────────────────────────────────────────────
    'loguru',
    'dotenv',
    'python_dotenv',

    # ── Torch ────────────────────────────────────────────────────────────────
    # Explicitly pre-load the sub-modules involved in the circular-import crash:
    #   torch.nested._internal.nested_tensor -> torch.autograd (not yet loaded)
    # The rthook-torch.py runtime hook handles the import ORDER fix;
    # these entries ensure the modules are present in the frozen bundle.
    'torch',
    'torch.autograd',
    'torch.autograd.profiler',
    'torch.nn',
    'torch.nn.functional',
    'torch.optim',
    'torch.utils',
    'torch.utils.data',
    'torch.nested',
    'torch.nested._internal',
    'torch.nested._internal.nested_tensor',
    'torchvision',
    'functorch',

    # ── Application packages ─────────────────────────────────────────────────
    'server',
    'server.server_main',
    'server.base',
    'server.cache',
    'server.config',
    'server.database',
    'server.database.db_session',
    'server.database.migrations',
    'server.database.models',
    'server.database.repository',
    'server.exceptions',
    'server.messages',
    'server.processor',
    'server.routes',
    'server.routes.chat_api_routes',
    'server.routes.chat_session_api_routes',
    'server.routes.file_api_routes',
    'server.routes.login_api_routes',
    'server.routes.model_provider_routes',
    'server.routes.settings_routes',
    'server.routes.user_api_routes',
    'server.routes.websocket_routes',
    'server.routes.websocket_stream_handler',
    'server.routes.message_router',
    'server.schemas',
    'server.service',
    'llm',
    'llm.LlmHandler',
    'llm.ToolHandler',
    'llm.agents',
    'llm.checkpoointer',
    'llm.configuration',
    'llm.embeddings',
    'llm.factory',
    'llm.inference_provider',
    'llm.integrations',
    'llm.interceptor',
    'llm.llm_handler',
    'llm.llm_messages',
    'llm.model_provider',
    'llm.prompts',
    'llm.services',
    'rag',
    'rag.factory',
    'rag.models',
    'rag.pipeline',
    'rag.prompts',
    'rag.retrievers',
    'vector_db',
    'vector_db.base',
    'vector_db.integrations',
    'utils',
    'base',
    'prompts',
    'model_downloader',
    'ssl_config',
]

# Collect all submodules dynamically for the big packages
for pkg in [
    'langchain', 'langchain_core', 'langchain_community', 'langchain_text_splitters',
    'langchain_aws', 'langchain_openai', 'langchain_anthropic',
    'langchain_together', 'langchain_ollama', 'langchain_google_genai',
    'langgraph', 'chromadb', 'sentence_transformers',
    'uvicorn', 'starlette', 'fastapi',
    'torch', 'torchvision',
    'ddgs',
    'primp',
]:
    hidden_imports += collect_submodules(pkg)

# =============================================================================
# Data files
# =============================================================================
datas = []

# ── Metadata (needed by some packages at runtime for version checks) ──────────
metadata_packages = [
    'langchain', 'langchain-core', 'langchain-community', 'langchain-text-splitters',
    'langchain-aws', 'langchain-openai', 'langchain-anthropic',
    'langchain-ollama', 'langchain-google-genai', 'langchain-mcp-adapters',
    'langgraph', 'langgraph-checkpoint-sqlite',
    'fastapi', 'uvicorn', 'starlette',
    'pydantic', 'pydantic-core',
    'chromadb',
    'sentence-transformers', 'transformers', 'tokenizers', 'huggingface-hub',
    'cryptography', 'certifi',
    'httpx', 'requests',
    'loguru', 'python-dotenv',
    'aiosqlite', 'duckdb', 'ddgs', 'primp',
    'beautifulsoup4', 'lxml',
]
for pkg in metadata_packages:
    try:
        datas += copy_metadata(pkg)
    except Exception:
        pass

# ── Package data files ─────────────────────────────────────────────────��──────
data_packages = [
    'langchain', 'langchain_core', 'langchain_community', 'langchain_text_splitters',
    'langgraph', 'chromadb',
    'sentence_transformers', 'transformers', 'tokenizers',
    'certifi',
    'starlette', 'fastapi',
]
for pkg in data_packages:
    try:
        datas += collect_data_files(pkg)
    except Exception:
        pass

# ── Bundled application data ──────────────────────────────────────────────────
# Embedding models shipped with the app
embedding_model_dir = os.path.join(ROOT, 'data', 'embedding_models')
if os.path.isdir(embedding_model_dir):
    datas += [(embedding_model_dir, os.path.join('data', 'embedding_models'))]

# SSL certificates (if pre-generated)
ssl_cert_dir = os.path.join(ROOT, 'data', 'ssl_certs')
if os.path.isdir(ssl_cert_dir):
    datas += [(ssl_cert_dir, os.path.join('data', 'ssl_certs'))]

# .env.example so users know which env vars are available
env_example = os.path.join(ROOT, '.env.example')
if os.path.isfile(env_example):
    datas += [(env_example, '.')]

# prompts directory (markdown / Python prompt files)
prompts_dir = os.path.join(ROOT, 'prompts')
if os.path.isdir(prompts_dir):
    datas += [(prompts_dir, 'prompts')]

# =============================================================================
# Collect primp binary (Rust native extension required by ddgs)
# =============================================================================
import glob, sysconfig
_primp_so = glob.glob(
    os.path.join(sysconfig.get_path('purelib'), 'primp', 'primp*.so')
) + glob.glob(
    os.path.join(sysconfig.get_path('purelib'), 'primp', 'primp*.dylib')
)
_primp_binaries = [(so, 'primp') for so in _primp_so]

# =============================================================================
# Analysis
# =============================================================================
a = Analysis(
    [os.path.join(ROOT, 'src', 'run_server.py')],
    pathex=[ROOT],
    binaries=_primp_binaries,
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=additional_hooks_dir,
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Test / dev tooling – keep the bundle lean
        # NOTE: do NOT exclude 'unittest' – torch.utils._config_module imports it
        'pytest',
        'IPython',
        'jupyter',
        'notebook',
        'matplotlib',
        'tkinter',
        '_tkinter',
    ],
    noarchive=False,
    optimize=0,
)

# =============================================================================
# PYZ archive
# =============================================================================
pyz = PYZ(a.pure)

# =============================================================================
# EXE
# =============================================================================
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PersonalAI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,       # keep True – this is a server process
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,   # None = native arch (arm64 on Apple Silicon)
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

# =============================================================================
# COLLECT  – produces dist/PersonalAI/ folder
# =============================================================================
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PersonalAI',
)

# =============================================================================
# macOS App Bundle  (optional – comment out if not needed)
# =============================================================================
app = BUNDLE(
    coll,
    name='PersonalAI.app',
    icon=None,
    bundle_identifier='com.personalai.server',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': True,
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'LSBackgroundOnly': True,       # headless server – no Dock icon
    },
)

