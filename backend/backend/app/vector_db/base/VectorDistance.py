from enum import Enum


class VectorDistance(str, Enum):
    """
    Type of internal tags, build from payload Distance function types used to compare vectors
    """

    def __str__(self) -> str:
        return str(self.value)

    COSINE = "Cosine"
    EUCLID = "Euclid"
    DOT = "Dot"
    MANHATTAN = "Manhattan"