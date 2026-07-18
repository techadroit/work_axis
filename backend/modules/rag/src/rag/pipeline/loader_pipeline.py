from docling.document_converter import DocumentConverter

from rag.pipeline.base_pipeline import BasePipeline
from core.utils.logger_util import log_debug


class LoadFilePipeline(BasePipeline):
    def __init__(self, file_path, next_steps=None):
        super().__init__(next_steps=next_steps)
        self.file_path = file_path

    def load(self):
        data = []
        converter = DocumentConverter()
        result = converter.convert(self.file_path).document
        result = result.export_to_markdown()
        data.append(result)
        print(result)
        return data

    def process(self, data=None, **kwargs):
        data = self.load()
        log_debug(f"data loaded from file:{kwargs['session_id']}")
        self._call_next(data=data, **kwargs)
