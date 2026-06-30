from pydantic.v1 import BaseModel


class Payload(BaseModel):
    document: str
    metadata: dict[str,str]

class VectorModel(BaseModel):
    embedding: list[float] = None
    payload: Payload
    distance: float = None
