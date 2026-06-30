from .base.vector_db_client import VectorDbClient
from .base.vector_db_config import VectorDbConfig
from .base.VectorDistance import VectorDistance
from .models.vector_model import VectorModel, Payload
from .vectordb_factory import VectorDBFactory

__all__ = [
    "VectorDbClient",
    "VectorDbConfig",
    "VectorDistance",
    "VectorModel",
    "Payload",
    "VectorDBFactory",
]


def main() -> None:
    print("vector-db module is installed and ready")
