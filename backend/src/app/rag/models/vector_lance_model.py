from lancedb.pydantic import LanceModel


class PayloadLance(LanceModel):
    document: str
    metadata: str  # Store as JSON string


class VectorLanceModel(LanceModel):
    embeddings: list[float]
    document: str
    metadata: str  # Store as JSON string
