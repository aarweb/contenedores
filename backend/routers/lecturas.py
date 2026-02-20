from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from routers.utils import parsear_object_id
from models.utils import TipoContador
from database import get_database
from models.lecturas import LecturaCreate, LecturaResponse
from motor.motor_asyncio import AsyncIOMotorDatabase


router = APIRouter(
    prefix="/lecturas",
    tags=["lecturas"],
    responses={
        404: {"description": "Lectura no encontrada"},
        400: {"description": "Error en la validación de negocio"},
        500: {"description": "Error interno del servidor o de conexión con MongoDB"},
    },
)


@router.post("/", response_model=LecturaResponse, status_code=status.HTTP_201_CREATED)
async def crear_lectura(
    lectura: LecturaCreate, db: AsyncIOMotorDatabase = Depends(get_database)
):
    contador = await db.contadores.find_one({"numero_serie": lectura.numero_serie})
    if not contador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró un contador con número de serie {lectura.numero_serie}",
        )

    if lectura.tipo != contador["tipo_suministro"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El tipo de lectura {lectura.tipo} no coincide con el tipo de suministro del contador ({contador['tipo_suministro']})",
        )

    ultima_lectura = await db.lecturas.find_one(
        {"contador_id": str(contador["_id"])}, sort=[("datos.fecha", -1)]
    )

    consumo_periodo = None
    if ultima_lectura:
        if lectura.tipo == "Electricidad":
            consumo_periodo = round(
                lectura.energia_activa_kwh
                - ultima_lectura["datos"]["energia_activa_kwh"],
                4,
            )
        elif lectura.tipo in ("Agua", "Gas"):
            consumo_periodo = round(
                lectura.volumen_acumulado_m3
                - ultima_lectura["datos"]["volumen_acumulado_m3"],
                4,
            )

    doc = {
        "contador_id": str(contador["_id"]),
        "consumo_periodo": consumo_periodo,
        "datos": lectura.model_dump(),
    }

    resultado = await db.lecturas.insert_one(doc)
    nueva_lectura = await db.lecturas.find_one({"_id": resultado.inserted_id})

    return nueva_lectura


@router.get("/contador/{contador_id}", response_model=list[LecturaResponse])
async def obtener_lecturas_por_contador(
    contador_id: str,
    skip: int = 0,
    limit: int = 20,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    object_id = parsear_object_id(contador_id)

    contador = await db.contadores.find_one({"_id": object_id})
    if not contador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró un contador con ID {contador_id}",
        )

    lecturas = (
        await db.lecturas.find({"contador_id": contador_id})
        .sort("datos.fecha", -1)
        .skip(skip)
        .limit(limit)
        .to_list(length=limit)
    )
    return lecturas


@router.get("/contador/{contador_id}/ultima", response_model=LecturaResponse)
async def obtener_ultima_lectura(
    contador_id: str, db: AsyncIOMotorDatabase = Depends(get_database)
):
    oid = parsear_object_id(contador_id)

    contador = await db.contadores.find_one({"_id": oid})
    if not contador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró ningún contador con el ID {contador_id}",
        )

    ultima = await db.lecturas.find_one(
        {"contador_id": contador_id}, sort=[("datos.fecha", -1)]
    )

    if not ultima:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay lecturas para el contador {contador_id}",
        )

    return ultima


@router.get("/contador/{contador_id}/consumo", response_model=dict)
async def obtener_consumo_periodo(
    contador_id: str,
    fecha_inicio: datetime,
    fecha_fin: datetime,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    oid = parsear_object_id(contador_id)

    contador = await db.contadores.find_one({"_id": oid})
    if not contador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró ningún contador con el ID {contador_id}",
        )

    lecturas = (
        await db.lecturas.find(
            {
                "contador_id": contador_id,
                "datos.fecha": {"$gte": fecha_inicio, "$lte": fecha_fin},
            }
        )
        .sort("datos.fecha", 1)
        .to_list(length=None)
    )

    if len(lecturas) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Se necesitan al menos 2 lecturas en el periodo para calcular el consumo",
        )

    primera = lecturas[0]
    ultima = lecturas[-1]

    # Calcular consumo según el tipo de suministro
    tipo = contador["tipo_suministro"]
    if tipo == TipoContador.ELECTRICIDAD.value:
        consumo = (
            ultima["datos"]["energia_activa_kwh"]
            - primera["datos"]["energia_activa_kwh"]
        )
        unidad = "kWh"
    else:  # Agua o Gas
        consumo = (
            ultima["datos"]["volumen_acumulado_m3"]
            - primera["datos"]["volumen_acumulado_m3"]
        )
        unidad = "m³"

    return {
        "contador_id": contador_id,
        "tipo_suministro": tipo,
        "fecha_inicio": primera["datos"]["fecha"],
        "fecha_fin": ultima["datos"]["fecha"],
        "num_lecturas": len(lecturas),
        "consumo": consumo,
        "unidad": unidad,
    }
