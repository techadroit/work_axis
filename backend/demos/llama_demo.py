import time

from langchain_community.llms import LlamaCpp
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler

from src.app.utils.logger_util import log_info, log_debug

# Callbacks support token-wise streaming
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
n_gpu_layers = -1  # The number of layers to put on the GPU. The rest will be on the CPU. If you don't know how many layers there are, you can use -1 to move all to GPU.
n_batch = 512

# Make sure the model path is correct for your system!
llm = LlamaCpp(
    model_path="../data/models/Mistral-7B-v0.3.Q8_0.gguf",
    temperature=0.75,
    max_tokens=2000,
    n_gpu_layers=n_gpu_layers,
    n_batch=n_batch,
    top_p=1
    # callback_manager=callback_manager,
    # verbose=True,  # Verbose is required to pass to the callback manager
)

question = """
Say a simple poem about a cat and a dog playing together
"""
# Measure execution time
start_time = time.time()
log_debug("model started")
response = llm.invoke(question)
end_time = time.time()
execution_time = end_time - start_time
log_info(f"Execution time: {execution_time:.2f} seconds")
log_info(response)
log_debug("model stopped")
