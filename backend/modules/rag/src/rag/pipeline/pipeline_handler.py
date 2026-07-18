from rag.pipeline.base_pipeline import BasePipeline


class PipelineHandler:
    def __init__(self, pipelines: list[BasePipeline]):
        self.pipelines = pipelines

    async def start(self, data=None, **kwargs):
        for pipeline in self.pipelines:
            pipeline.process(data, **kwargs)


def create_pipeline_handler(pipelines: list[BasePipeline]) -> PipelineHandler:
    return PipelineHandler(pipelines)