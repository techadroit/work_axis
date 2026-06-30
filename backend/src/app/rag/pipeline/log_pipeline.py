from src.app.rag.pipeline.base_pipeline import BasePipeline
from src.app.utils.logger_util import log_debug


class LogPipeline(BasePipeline):

    def process(self, data=None, **kwargs):
        log_debug("LogPipeline process")