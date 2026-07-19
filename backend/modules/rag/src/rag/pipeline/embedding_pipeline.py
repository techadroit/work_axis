from rag.models.vector_model import VectorModel, Payload
from rag.pipeline.base_pipeline import BasePipeline
from src.app.utils.embedding_util import get_cached_default_embedding_model
from core.utils.logger_util import log_debug


class EmbeddingPipeline(BasePipeline):

    def __init__(self, next_steps=None):
        super().__init__(next_steps)

    def process(self, data=None, **kwargs):
        session_id = kwargs.get('session_id')
        user_id = kwargs.get('user_id')
        log_debug(f"embedding started {user_id} and {session_id}")
        metadata = {}
        if session_id is not None:
            metadata = {"session_id": session_id, "user_id": user_id}
        embedding_model = get_cached_default_embedding_model()
        result = []
        for document in data:
            embeddings = embedding_model.embed_documents([document])
            model = VectorModel(embedding=embeddings[0], payload=Payload(document=document, metadata=metadata))
            result.append(model)
        self._call_next(data=result,**kwargs)
