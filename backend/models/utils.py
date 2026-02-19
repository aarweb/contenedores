import enum
from typing import Any
from bson import ObjectId


class TipoContador(enum.Enum):
    AGUA = "Agua"
    ELECTRICIDAD = "Electricidad"
    GAS = "Gas"


def validar_object_id(v: Any) -> str:
    if isinstance(v, ObjectId):
        return str(v)
    if isinstance(v, str):
        return v
    raise ValueError("ObjectID invalido")
