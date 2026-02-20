import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import os
import random

from fastapi import FastAPI
import httpx
from pydantic import BaseModel, Field

CONTADOR_ID = os.getenv("CONTADOR_ID")
NUMERO_SERIE = os.getenv("NUMERO_SERIE", "SN-???")
TIPO_SUMINISTRO = os.getenv("TIPO_SUMINISTRO")
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
INTERVALO_SEG = float(os.getenv("INTERVALO_SEG", "60"))
PORT = int(os.getenv("PORT", "8001"))

state = {
    "activo": False,
    "intervalo_seg": INTERVALO_SEG,
    "pulsos_enviados": 0,
    "ultimo_pulso": None,
    "ultimo_error": None,
    "acumulado": round(random.uniform(100, 5000), 3),
}

_tarea_pulso: asyncio.Task | None = None


def _generar_lectura_electricidad(
    acumulado: float, intervalo_h: float
) -> tuple[dict, float]:
    """
    Genera una lectura simulada de electricidad, con consumo basado en el intervalo y acumulado actualizado.
    """
    consumo = round(random.uniform(0.5, 4.0) * intervalo_h, 4)
    acumulado += consumo
    return {
        "tipo_suministro": "Electricidad",
        "consumo_periodo": round(consumo, 4),
        "energia_activa_kwh": round(acumulado, 3),
        "energia_reactiva_kvarh": round(acumulado * 0.14, 3),
        "potencia_activa_kw": round(random.uniform(1.0, 5.0), 3),
        "potencia_reactiva_kvar": round(random.uniform(0.1, 0.8), 3),
        "voltaje_v": round(random.uniform(228, 232), 2),
        "corriente_a": round(random.uniform(4, 22), 2),
        "factor_potencia": round(random.uniform(0.92, 0.99), 3),
        "frecuencia_hz": round(random.uniform(49.95, 50.05), 3),
    }, acumulado


def _generar_lectura_agua(acumulado: float, intervalo_h: float) -> tuple[dict, float]:
    """
    Genera una lectura simulada de agua, con consumo basado en el intervalo y acumulado actualizado.
    """
    consumo = round(random.uniform(0.05, 0.5) * intervalo_h, 4)
    acumulado += consumo
    return {
        "tipo_suministro": "Agua",
        "consumo_periodo": round(consumo, 4),
        "volumen_acumulado_m3": round(acumulado, 3),
        "caudal_m3h": round(random.uniform(0.1, 1.2), 3),
        "presion_bar": round(random.uniform(2.5, 4.0), 2),
        "temperatura_c": round(random.uniform(10, 20), 1),
    }, acumulado


def _generar_lectura_gas(acumulado: float, intervalo_h: float) -> tuple[dict, float]:
    """
    Genera una lectura simulada de gas, con consumo basado en el intervalo y acumulado actualizado.
    """
    consumo = round(random.uniform(0.1, 1.5) * intervalo_h, 4)
    acumulado += consumo
    return {
        "tipo_suministro": "Gas",
        "consumo_periodo": round(consumo, 4),
        "volumen_acumulado_m3": round(acumulado, 3),
        "caudal_m3h": round(random.uniform(0.3, 2.0), 3),
        "presion_mbar": round(random.uniform(19, 25), 2),
        "temperatura_c": round(random.uniform(6, 15), 1),
        "poder_calorifico_kwh_m3": round(random.uniform(10.5, 11.5), 3),
    }, acumulado


def _generar_lectura() -> dict:
    """
    Genera una lectura simulada segun el tipo de suministro
    """
    intervalo_h = state["intervalo_seg"] / 3600
    tipo = TIPO_SUMINISTRO

    if tipo == "Electricidad":
        datos, nuevo_acum = _generar_lectura_electricidad(
            state["acumulado"], intervalo_h
        )
    elif tipo == "Agua":
        datos, nuevo_acum = _generar_lectura_agua(state["acumulado"], intervalo_h)
    elif tipo == "Gas":
        datos, nuevo_acum = _generar_lectura_gas(state["acumulado"], intervalo_h)
    else:
        raise ValueError(f"Tipo de suministro desconocido: {tipo}")

    state["acumulado"] = nuevo_acum
    return {
        "numero_serie": NUMERO_SERIE,
        "fecha": datetime.now(timezone.utc).isoformat(),
        "tipo": TIPO_SUMINISTRO,
        **{
            k: v
            for k, v in datos.items()
            if k not in ("tipo_suministro", "consumo_periodo")
        },
    }


async def _bucle_pulsos():
    """
    Bucle asincrono donde, genera la lectura simulada y la envia al backend segun el intervalo configurado.
    Actualiza el estado con el número de pulsos enviados, fecha del último pulso y cualquier error ocurrido.
    """
    async with httpx.AsyncClient(timeout=10) as client:
        while state["activo"]:
            try:
                lectura = _generar_lectura()
                res = await client.post(
                    f"{BACKEND_URL}/lecturas/",
                    json=lectura,
                )
                res.raise_for_status()
                state["pulsos_enviados"] += 1
                state["ultimo_pulso"] = datetime.now(timezone.utc).isoformat()
                state["ultimo_error"] = None
                print(f"[{NUMERO_SERIE}] Pulso #{state['pulsos_enviados']} enviado")
            except Exception as e:
                state["ultimo_error"] = str(e)
                print(f"[{NUMERO_SERIE}] Error al enviar pulso: {e}")

            await asyncio.sleep(state["intervalo_seg"])


def _iniciar_tarea():
    """
    Inicia o reinicia la tarea asincrona que emite los pulsos.
    Si ya hay una tarea en ejecución, se cancela antes de iniciar una nueva para aplicar
    """
    global _tarea_pulso
    if _tarea_pulso and not _tarea_pulso.done():
        _tarea_pulso.cancel()
    _tarea_pulso = asyncio.create_task(_bucle_pulsos())


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Inicia el bucle de pulsos al levantar el contenedor y lo detiene al apagarlo.
    Si CONTADOR_ID y TIPO_SUMINISTRO están configurados, el simulador inicia, si no, no inicia y se tendra que levantar
    manualmente a través del endpoint /start
    """
    if CONTADOR_ID and TIPO_SUMINISTRO:
        state["activo"] = True
        _iniciar_tarea()
        print(
            f"[{NUMERO_SERIE}] Simulador iniciado — tipo={TIPO_SUMINISTRO}, intervalo={INTERVALO_SEG}s"
        )
    else:
        print(
            f"[{NUMERO_SERIE}] CONTADOR_ID o TIPO_SUMINISTRO no configurados — arranque manual requerido"
        )
    yield
    state["activo"] = False
    if _tarea_pulso:
        _tarea_pulso.cancel()


app = FastAPI(title="Contadores API", version="1.0.0", lifespan=lifespan)


class SetFrequencyRequest(BaseModel):
    """
    Modelo para la petición de cambio de frecuencia
    """

    intervalo_seg: float = Field(
        ..., ge=5, description="Intervalo mínimo de 5 segundos"
    )


@app.get("/status")
async def status():
    """
    Metodo para obtener el estado actual del contador.
    """
    return {
        "numero_serie": NUMERO_SERIE,
        "contador_id": CONTADOR_ID,
        "tipo_suministro": TIPO_SUMINISTRO,
        "backend_url": BACKEND_URL,
        "activo": state["activo"],
        "intervalo_seg": state["intervalo_seg"],
        "pulsos_enviados": state["pulsos_enviados"],
        "ultimo_pulso": state["ultimo_pulso"],
        "ultimo_error": state["ultimo_error"],
        "acumulado": state["acumulado"],
    }


@app.post("/set-frequency")
async def set_frequency(body: SetFrequencyRequest):
    """
    Cambiar el intervalo de envio de lecturas, como minimo 5 segundos.
    """
    state["intervalo_seg"] = body.intervalo_seg

    # Reinicia la tarea para que el nuevo intervalo tenga efecto inmediato
    if state["activo"]:
        _iniciar_tarea()

    return {
        "ok": True,
        "intervalo_seg": state["intervalo_seg"],
        "mensaje": f"Frecuencia actualizada a 1 pulso cada {body.intervalo_seg}s",
    }


@app.post("/start")
async def start():
    """
    Inicia el envio de pulsos si no está activa.
    """
    if not CONTADOR_ID or not TIPO_SUMINISTRO:
        return {"error": "CONTADOR_ID y TIPO_SUMINISTRO son obligatorios"}
    if state["activo"]:
        return {"ok": True, "mensaje": "El simulador ya estaba activo"}

    state["activo"] = True
    _iniciar_tarea()
    return {"ok": True, "mensaje": "Simulador iniciado"}


@app.post("/stop")
async def stop():
    """
    Para el envio de pulsos si está activo.
    """
    state["activo"] = False
    if _tarea_pulso:
        _tarea_pulso.cancel()
    return {"ok": True, "mensaje": "Simulador detenido"}
