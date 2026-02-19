from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.clientes import ClienteCreate, ClienteResponse, ClienteUpdate
from database.database import get_database
from routers.utils import parsear_object_id

router = APIRouter(
    prefix="/clientes",
    tags=["contadores"],
    responses={
        404: {"description": "Cliente no encontrado"},
        400: {"description": "Error en la validacion de negocio"},
        500: {"description": "Error interno del servidor ode conexión con MongoDB"},
    },
)


@router.post("/", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
async def crear_cliente(
    cliente: ClienteCreate, db: AsyncIOMotorDatabase = Depends(get_database)
):
    cliente_existente = await db.clientes.find_one({"email": cliente.email})

    if cliente_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un cliente con el email {cliente.email}",
        )

    doc = cliente.model_dump()
    doc["fecha_registro"] = datetime.now()

    resultado = await db.clientes.insert_one(doc)

    nuevo_cliente = await db.clientes.find_one({"_id": resultado.inserted_id})
    return nuevo_cliente


@router.get("/", response_model=list[ClienteResponse])
async def obtener_clientes(
    skip: int = 0, limit: int = 20, db: AsyncIOMotorDatabase = Depends(get_database)
):
    clientes = await db.clientes.find().skip(skip).limit(limit).to_list(length=limit)
    return clientes


@router.get("/{cliente_id}", response_model=ClienteResponse)
async def obtener_cliente(
    cliente_id: str, db: AsyncIOMotorDatabase = Depends(get_database)
):
    object_id = parsear_object_id(cliente_id)

    cliente = await db.clientes.find_one({"_id": object_id})

    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró un cliente con ID {cliente_id}",
        )

    return cliente


@router.put("/{cliente_id}", response_model=ClienteResponse)
async def actualizar_cliente(
    cliente_id: str,
    cliente: ClienteUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    object_id = parsear_object_id(cliente_id)

    datos = {
        key: value for key, value in cliente.model_dump().items() if value is not None
    }

    if not datos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se proporcionaron campos para actualizar",
        )

    resultado = await db.clientes.update_one({"_id": object_id}, {"$set": datos})

    if resultado.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró un cliente con ID {cliente_id}",
        )

    cliente_actualizado = await db.clientes.find_one({"_id": object_id})
    return cliente_actualizado


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_cliente(
    cliente_id: str, db: AsyncIOMotorDatabase = Depends(get_database)
):
    object_id = parsear_object_id(cliente_id)

    resultado = await db.clientes.delete_one({"_id": object_id})

    if resultado.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró un cliente con ID {cliente_id}",
        )
