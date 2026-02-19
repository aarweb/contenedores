from bson import ObjectId
from fastapi import HTTPException, status


def parsear_object_id(id: str) -> ObjectId:
    try:
        return ObjectId(id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ID inválido: {id}. Debe ser un ObjectId válido.",
        )
