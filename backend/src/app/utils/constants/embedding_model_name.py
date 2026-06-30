# Shim – re-exports from core so existing imports keep working unchanged.
from core.utils.constants.embedding_model_name import EmbeddingModelName  # noqa: F401

    # OpenAI Models
    TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"
    TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"
    TEXT_EMBEDDING_ADA_002 = "text-embedding-ada-002"

    # Google Models
    UNIVERSAL_SENTENCE_ENCODER = "universal-sentence-encoder"
    EMBEDDING_GEMMA_LATEST = "embeddinggemma:latest"

    # BERT-based Models
    BERT_EMBEDDINGS = "bert-embeddings"

    # Sentence-BERT / SBERT Models
    ALL_MINILM_L6_V2 = "all-MiniLM-L6-v2"
    ALL_MINILM = "all-minilm"

    # Microsoft Models
    MPNET = "mpnet"
    MINILM = "minilm"

    # RoBERTa Models
    ROBERTA_EMBEDDINGS = "roberta-embeddings"

    # Meta Models
    LASER = "laser"
    LLAMA_EMBEDDINGS = "llama-embeddings"
    DINO = "dino"  # Vision model

    # AI21 Labs Models
    AI21_EMBEDDING = "ai21-embedding"

    # Cohere Models
    EMBED_ENGLISH_V2_0 = "embed-english-v2.0"
    EMBED_MULTILINGUAL_V2_0 = "embed-multilingual-v2.0"

    # Mistral Models
    MISTRAL_EMBEDDINGS = "mistral-embeddings"

    # AWS Models
    TITAN_EMBEDDINGS = "titan-embeddings"

    # Alibaba Models
    TONGYI_EMBEDDINGS = "tongyi-embeddings"

    # Multilingual Models
    LABSE = "labse"

    # Classic Word Embeddings
    GLOVE = "glove"
    WORD2VEC = "word2vec"
    FASTTEXT = "fasttext"

    # Vision and Text Models
    CLIP = "clip"  # OpenAI, for vision and text

    # Ollama Models
    MXBAI_EMBED_LARGE = "mxbai-embed-large"
    NOMIC_EMBED_TEXT = "nomic-embed-text"

