import os
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("DATABASE_URL")
DB_NAME = os.getenv("DB_NAME", "servicio_contador")


class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None


db_client = MongoDB()


async def connect_to_mongo():
    """Inicializa la conexión."""
    try:
        db_client.client = AsyncIOMotorClient(MONGO_URL)
        db_client.db = db_client.client[DB_NAME]

        await db_client.client.admin.command("ping")
    except Exception as e:
        raise e


async def close_mongo_connection():
    """Cierra la conexión."""
    if db_client.client:
        db_client.client.close()


def get_database() -> AsyncIOMotorDatabase:
    """Devuelve la instancia de la base de datos con validación de tipo."""
    if db_client.db is None:
        raise RuntimeError("La base de datos no ha sido inicializada")
    return db_client.db
