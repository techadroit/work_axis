from src.app.llm.inference_provider.inference_provider import InferenceProvider


class AwsInferenceProvider(InferenceProvider):

    def __init__(self, region_name, aws_access_key, aws_secret_access_key):
        self.region_name = region_name
        self.aws_access_key = aws_access_key
        self.aws_secret_access_key = aws_secret_access_key
