from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, BeforeValidator, EmailStr, Field

from .utils import validar_object_id


class ClienteBase(BaseModel):
    nombre: str
    apellidos: str
    email: EmailStr
    telefono: str
    direccion_facturacion: str


class ClienteCreate(ClienteBase):
    pass


class ClienteResponse(ClienteBase):
    id: Annotated[str, BeforeValidator(validar_object_id)] = Field(alias="_id")
    fecha_registro: datetime

    class Config:
        # Nos permite acceder al campo 'id' usando su alias '_id'
        populate_by_name = True


class ClienteUpdate(BaseModel):
    nombre: str | None = None
    apellidos: str | None = None
    email: EmailStr | None = None
    telefono: str | None = None
    direccion_facturacion: str | None = None
