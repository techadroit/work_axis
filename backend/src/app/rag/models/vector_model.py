# Shim – re-exports from the vector_db module so existing imports keep working unchanged.
from vector_db.models.vector_model import (  # noqa: F401
    Payload,
    VectorModel,
)
