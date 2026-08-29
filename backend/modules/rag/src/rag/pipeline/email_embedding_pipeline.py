import uuid

from rag.models.vector_model import VectorModel, Payload
from rag.pipeline.base_pipeline import BasePipeline
from src.app.utils.embedding_util import get_cached_default_embedding_model
from core.utils.logger_util import log_debug

# Fixed namespace for deriving deterministic per-chunk vector ids from
# (email_account_id, message_id, chunk_index). Any fixed UUID works here -
# it only needs to be stable across process restarts, unlike uuid4().
_EMAIL_ID_NAMESPACE = uuid.UUID("6f2a9c2e-6b7d-4b8e-9f0a-1c2d3e4f5a6b")


class EmailEmbeddingPipeline(BasePipeline):
    """Embeds email chunks and attaches email-specific metadata.

    Sibling to EmbeddingPipeline, but:
    - takes an `email_metadata` dict (already-stringified: source,
      user_id, email_account_id, message_id, from, subject, date) instead
      of session_id/user_id
    - computes a deterministic vector id per chunk so re-ingesting the same
      email on a resync overwrites (upsert) instead of duplicating
    """

    def __init__(self, next_steps=None):
        super().__init__(next_steps)

    def process(self, data=None, **kwargs):
        email_metadata = kwargs.get("email_metadata") or {}
        email_account_id = email_metadata.get("email_account_id", "")
        message_id = email_metadata.get("message_id", "")
        log_debug(f"email embedding started for message_id={message_id}")

        embedding_model = get_cached_default_embedding_model()
        result = []
        for chunk_index, chunk in enumerate(data):
            embeddings = embedding_model.embed_documents([chunk])
            metadata = {**email_metadata, "chunk_index": str(chunk_index)}
            vector_id = str(uuid.uuid5(
                _EMAIL_ID_NAMESPACE, f"{email_account_id}:{message_id}:{chunk_index}"
            ))
            model = VectorModel(
                embedding=embeddings[0],
                payload=Payload(document=chunk, metadata=metadata),
                id=vector_id,
            )
            result.append(model)
        self._call_next(data=result, **kwargs)
