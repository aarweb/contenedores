from fastapi import FastAPI
from contextlib import asynccontextmanager
from routers import contadores_router, clientes_router
from database import connect_to_mongo, close_mongo_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Metodo que inicia o cierra mongodb al iniciar o parar el backend
    """
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(title="Servicio Contadores", lifespan=lifespan)

app.include_router(contadores_router)
app.include_router(clientes_router)
