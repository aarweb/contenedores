import os
import time
import random
from typing import Any, Dict
import requests
import logging

# Configuración de logs
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("Contador")

API_URL = os.getenv("API_URL", "http://backend:8000/lecturas/")
NUMERO_SERIE = os.getenv("NUMERO_SERIE", "UNKNOWN-000")
TIPO_SUMINISTRO = os.getenv("TIPO_SUMINISTRO", "Electricidad")
INTERVALO = int(os.getenv("INTERVALO_ENVIO", "10"))


def generar_datos():
    """Genera datos simulados según el tipo de contador."""

    datos: Dict[str, Any] = {
        "numero_serie": NUMERO_SERIE,
        "tipo": TIPO_SUMINISTRO,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    if TIPO_SUMINISTRO == "Electricidad":
        datos["valor"] = round(random.uniform(0.5, 5.0), 3)
        datos["unidad"] = "kWh"
        datos["voltaje"] = round(random.uniform(220, 240), 1)
    elif TIPO_SUMINISTRO == "Agua":
        datos["valor"] = round(random.uniform(10, 500), 2)
        datos["unidad"] = "L"
        datos["presion"] = round(random.uniform(2, 4), 1)
    else:  # Gas
        datos["valor"] = round(random.uniform(0.1, 2.0), 3)
        datos["unidad"] = "m3"
        datos["temperatura"] = round(random.uniform(15, 25), 1)

    return datos


def ciclo_principal():
    logger.info(f"Iniciando contador {NUMERO_SERIE} ({TIPO_SUMINISTRO})...")
    logger.info(f"Enviando datos a: {API_URL}")

    while True:
        try:
            payload = generar_datos()
            response = requests.post(API_URL, json=payload, timeout=5)

            if response.status_code in [200, 201]:
                logger.info(
                    f"✅ Lectura enviada: {payload['valor']} {payload.get('unidad')}"
                )
            else:
                logger.warning(f"⚠️ Error API {response.status_code}: {response.text}")

        except requests.exceptions.ConnectionError:
            logger.error("❌ No se puede conectar con la API. Reintentando...")
        except Exception as e:
            logger.error(f"❌ Error inesperado: {e}")

        time.sleep(INTERVALO)


if __name__ == "__main__":
    ciclo_principal()
