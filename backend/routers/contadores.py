from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from routers.utils import parsear_object_id
from models.utils import TipoContador
from models.contadores import (
    ContadorCreate,
    ContadorResponse,
    ContadorUpdate,
    EstadoContador,
)
from database.database import get_database
from services.docker_manager import (
    iniciar_contenedor,
    detener_contenedor,
    estado_contenedor,
    listar_contenedores_contadores,
)


router = APIRouter(
    prefix="/contadores",
    tags=["contadores"],
    responses={
        404: {"description": "Contador no encontrado"},
        400: {"description": "Error en la validación de negocio"},
        500: {"description": "Error interno del servidor o de conexión con MongoDB"},
    },
)


@router.post("/", response_model=ContadorResponse, status_code=status.HTTP_201_CREATED)
async def crear_contador(
    contador: ContadorCreate, db: AsyncIOMotorDatabase = Depends(get_database)
):
    contador_existente = await db.contadores.find_one(
        {
            "$or": [
                {"numero_serie": contador.numero_serie},
                {"cups_poliza": contador.cups_poliza},
            ]
        }
    )

    if contador_existente:
        if contador_existente["numero_serie"] == contador.numero_serie:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un contador con el número de serie {contador.numero_serie}",
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un contador con el CUPS/póliza {contador.cups_poliza}",
        )

    doc = contador.model_dump()
    doc["fecha_instalacion"] = datetime.now()
    doc["clientes"] = []

    result = await db.contadores.insert_one(doc)

    nuevo_contador = await db.contadores.find_one({"_id": result.inserted_id})

    # Levantar contenedor Docker automáticamente
    try:
        iniciar_contenedor(
            contador_id=str(result.inserted_id),
            numero_serie=contador.numero_serie,
            tipo_suministro=doc["tipo_suministro"],
        )
    except Exception as e:
        print(f"[contadores] Error al levantar contenedor: {e}")

    return nuevo_contador


@router.get("/", response_model=List[ContadorResponse])
async def obtener_contadores(
    skip: int = 0,
    limit: int = 20,
    tipo: TipoContador | None = None,
    estado: EstadoContador | None = None,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    filtro = {}
    if tipo:
        filtro["tipo_suministro"] = tipo.value
    if estado:
        filtro["estado"] = estado.value

    contadores = (
        await db.contadores.find(filtro).skip(skip).limit(limit).to_list(length=limit)
    )
    return contadores


@router.get("/{contador_id}", response_model=ContadorResponse)
async def obtener_contador(
    contador_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    object_id = parsear_object_id(contador_id)

    contador = await db.contadores.find_one({"_id": object_id})

    if not contador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró un contador con ID {contador_id}",
        )

    return contador


@router.put("/{contador_id}", response_model=ContadorResponse)
async def actualizar_contador(
    contador_id: str,
    contador: ContadorUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    object_id = parsear_object_id(contador_id)

    datos = {
        key: value for key, value in contador.model_dump().items() if value is not None
    }

    if not datos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se proporcionaron campos para actualizar",
        )

    resultado = await db.contadores.update_one({"_id": object_id}, {"$set": datos})

    if resultado.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró un contador con ID {contador_id}",
        )

    contador_actualizado = await db.contadores.find_one({"_id": object_id})
    return contador_actualizado


@router.delete("/{contador_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_contador(
    contador_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    object_id = parsear_object_id(contador_id)

    resultado = await db.contadores.delete_one({"_id": object_id})

    if resultado.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró un contador con ID {contador_id}",
        )

    try:
        detener_contenedor(contador_id)
    except Exception as e:
        print(f"[contadores] Error al detener contenedor: {e}")


@router.get("/{contador_id}/contenedor")
async def obtener_estado_contenedor(contador_id: str):
    """Devuelve el estado del contenedor Docker asociado a un contador."""
    info = estado_contenedor(contador_id)
    if not info:
        return {
            "status": "no_container",
            "mensaje": "No hay contenedor para este contador",
        }
    return info


@router.get("/contenedores/todos")
async def listar_contenedores():
    """Lista todos los contenedores de contadores activos."""
    return listar_contenedores_contadores()


@router.post("/{contador_id}/clientes/{cliente_id}", status_code=status.HTTP_200_OK)
async def asignar_cliente(
    contador_id: str,
    cliente_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    contador_oid = parsear_object_id(contador_id)
    cliente_oid = parsear_object_id(cliente_id)

    contador = await db.contadores.find_one({"_id": contador_oid})
    if not contador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró un contador con ID {contador_id}",
        )

    cliente = await db.clientes.find_one({"_id": cliente_oid})
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró un cliente con ID {cliente_id}",
        )

    if cliente_oid in contador.get("clientes", []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El cliente con ID {cliente_id} ya está asignado al contador {contador_id}",
        )

    await db.contadores.update_one(
        {"_id": contador_oid},
        {"$push": {"clientes": cliente_oid}},
    )


@router.delete(
    "/{contador_id}/clientes/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def desasignar_cliente(
    contador_id: str,
    cliente_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    contador_oid = parsear_object_id(contador_id)
    cliente_oid = parsear_object_id(cliente_id)

    contador = await db.contadores.find_one({"_id": contador_oid})
    if not contador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró un contador con ID {contador_id}",
        )

    cliente = await db.clientes.find_one({"_id": cliente_oid})
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró un cliente con ID {cliente_id}",
        )

    if cliente_oid not in contador.get("clientes", []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El cliente con ID {cliente_id} no está asignado al contador {contador_id}",
        )

    await db.contadores.update_one(
        {"_id": contador_oid},
        {"$pull": {"clientes": cliente_oid}},
    )
