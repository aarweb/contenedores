from datetime import datetime
import enum
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

from .utils import TipoContador, validar_object_id


class EstadoContador(enum.Enum):
    ACTIVO = "Activo"
    AVERIADO = "Averiado"
    SABOTEADO = "Saboteado"


class ContadorBase(BaseModel):
    numero_serie: str = Field(..., min_length=5)
    cups_poliza: str
    marca: str
    modelo: str
    version_firmware: str
    latitud: float = Field(..., ge=-90, le=90)
    longitud: float = Field(..., ge=-180, le=180)
    direccion_fisica: str
    tipo_suministro: TipoContador
    estado: EstadoContador = Field(default=EstadoContador.ACTIVO)

    model_config = ConfigDict(use_enum_values=True)


class ContadorCreate(ContadorBase):
    pass


class ContadorUpdate(BaseModel):
    cups_poliza: str | None = None
    marca: str | None = None
    modelo: str | None = None
    version_firmware: str | None = None
    latitud: float | None = Field(default=None, ge=-90, le=90)
    longitud: float | None = Field(default=None, ge=-180, le=180)
    direccion_fisica: str | None = None
    estado: EstadoContador | None = None

    model_config = ConfigDict(use_enum_values=True)


class ContadorResponse(ContadorBase):
    id: Annotated[str, BeforeValidator(validar_object_id)] = Field(alias="_id")
    fecha_instalacion: datetime
    clientes: list[Annotated[str, BeforeValidator(validar_object_id)]] = Field(
        default_factory=list
    )

    model_config = ConfigDict(
        # Nos permite acceder al campo 'id' usando su alias '_id'
        populate_by_name=True,
        use_enum_values=True,
    )
