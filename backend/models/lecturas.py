from datetime import datetime
from typing import Annotated, Literal, Union
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

from .utils import TipoContador, validar_object_id


class LecturaBase(BaseModel):
    numero_serie: str
    fecha: datetime


class LecturaElectricidad(LecturaBase):
    tipo: Literal["Electricidad"] = "Electricidad"
    energia_activa_kwh: float = Field(
        ..., ge=0, description="Energía activa acumulada (kWh)"
    )

    energia_reactiva_kvarh: float = Field(
        ..., ge=0, description="Energía reactiva acumulada (kVArh)"
    )

    potencia_activa_kw: float = Field(
        ..., ge=0, description="Potencia activa instantánea (kW)"
    )

    potencia_reactiva_kvar: float = Field(
        ..., description="Potencia reactiva instantánea (kVAr)"
    )

    voltaje_v: float = Field(..., ge=0, le=500, description="Tensión de línea (V)")
    corriente_a: float = Field(..., ge=0, description="Intensidad de corriente (A)")
    factor_potencia: float = Field(..., ge=-1, le=1, description="Factor de potencia")
    frecuencia_hz: float = Field(
        ..., ge=49, le=51, description="Frecuencia de red (Hz)"
    )


class LecturaAgua(LecturaBase):
    tipo: Literal["Agua"] = "Agua"

    volumen_acumulado_m3: float = Field(..., ge=0, description="Volumen acumulado (m³)")
    caudal_m3h: float = Field(..., ge=0, description="Caudal instantáneo (m³/h)")
    presion_bar: float = Field(..., ge=0, description="Presión del agua (bar)")
    temperatura_c: float = Field(
        ..., ge=0, le=100, description="Temperatura del agua (°C)"
    )


class LecturaGas(LecturaBase):
    tipo: Literal["Gas"] = "Gas"

    volumen_acumulado_m3: float = Field(
        ..., ge=0, description="Volumen acumulado en condiciones reales (m³)"
    )
    caudal_m3h: float = Field(..., ge=0, description="Caudal instantáneo (m³/h)")
    presion_mbar: float = Field(..., ge=0, description="Presión del gas (mbar)")
    temperatura_c: float = Field(
        ..., ge=-20, le=60, description="Temperatura del gas (°C)"
    )
    poder_calorifico_kwh_m3: float = Field(
        ..., ge=0, description="Poder calorífico (kWh/m³)"
    )


LecturaCreate = Annotated[
    Union[LecturaElectricidad, LecturaAgua, LecturaGas], Field(discriminator="tipo")
]


class LecturaResponse(BaseModel):
    id: Annotated[str, BeforeValidator(validar_object_id)] = Field(alias="_id")
    contador_id: Annotated[str, BeforeValidator(validar_object_id)]
    consumo_periodo: float | None = None
    datos: Union[LecturaElectricidad, LecturaAgua, LecturaGas] = Field(
        discriminator="tipo"
    )

    model_config = ConfigDict(populate_by_name=True)
