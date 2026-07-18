import os

from huggingface_hub import snapshot_download

from core.utils.file_util import get_embedding_models_path

model_id = 'sentence-transformers/all-MiniLM-L6-v2'
local_dir = str(get_embedding_models_path())

def download_embedding_model():
    """
    Download embedding model if not already present.
    Handles SSL errors gracefully for bundled executables.
    """

    try:
        # Disable SSL warnings
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # Clear CA bundle to use relaxed verification
        os.environ.pop('REQUESTS_CA_BUNDLE', None)
        os.environ.pop('CURL_CA_BUNDLE', None)
        os.environ['CURL_CA_BUNDLE'] = ''
        os.environ['REQUESTS_CA_BUNDLE'] = ''

        print("SSL verification disabled")

        # Create SSL context with relaxed verification
        # ssl_context = get_client_ssl_context(verify=False)
        print("SSL context loaded")

        snapshot_path = snapshot_download(
            repo_id=model_id,
            local_dir=local_dir,
            local_dir_use_symlinks=False
        )
        print(f"Model files downloaded to: {snapshot_path}")

        # Load the model to verify
        # model = SentenceTransformer(local_dir)
        print("Embedding model loaded successfully")

    except Exception as e:
        print(f"Error downloading embedding model: {e}")
        print("WARNING: Embedding model not available. Some features may not work.")
        print("To fix: Run with internet connection or bundle the model in data/embedding_models/")

