from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.app.rag.pipeline.base_pipeline import BasePipeline
from backend.app.utils.logger_util import log_debug
from sentence_transformers import SentenceTransformer



class ChunkingPipeline(BasePipeline):

    def __init__(self, next_steps=None):
        super().__init__(next_steps=next_steps)

    def process(self, data=None, **kwargs):
        for chunks in data:
            result = self.chunk(chunks)
            self._call_next(data=result,**kwargs)

    def chunk(self, data):
        log_debug("Chunking started")
        splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=51)
        result = splitter.split_text(data)

        return result
