from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import httpx
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contadores_router)
app.include_router(clientes_router)


@app.get("/geocode/")
async def geocode_proxy(q: str = Query(...), limit: int = Query(1)):
    """Proxy para Nominatim que evita problemas de CORS en el navegador."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://nominatim.openstreetmap.org/search",
            params={"format": "json", "q": q, "limit": limit},
            headers={
                "User-Agent": "ContadoresApp/1.0",
                "Accept-Language": "es",
            },
        )
        resp.raise_for_status()
        return resp.json()
