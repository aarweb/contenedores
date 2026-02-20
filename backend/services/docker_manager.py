import os
import docker
from docker.errors import NotFound, APIError

CONTADOR_IMAGE = os.getenv("CONTADOR_IMAGE", "contadores-contador")
DOCKER_NETWORK = os.getenv("DOCKER_NETWORK", "contadores_db_network")
BACKEND_URL_INTERNAL = os.getenv("BACKEND_URL_INTERNAL", "http://backend:8000")
INTERVALO_SEG = os.getenv("INTERVALO_SEG", "60")

_client: docker.DockerClient | None = None


def _get_client() -> docker.DockerClient:
    """
    Obtiene la instancia del cliente de docker
    """
    global _client
    if _client is None:
        _client = docker.from_env()
    return _client


def _container_name(contador_id: str) -> str:
    """
    Generar un nombre del contenedor con el Object Id del contador que ha generado mongo
    """
    return f"contador-{contador_id}"


def iniciar_contenedor(
    contador_id: str,
    numero_serie: str,
    tipo_suministro: str,
) -> dict:
    """
    Crea y arranca un contenedor para el contador dado.
    Devuelve info básica del contenedor.
    """
    client = _get_client()
    name = _container_name(contador_id)

    try:
        existing = client.containers.get(name)
        if existing.status != "running":
            existing.start()
        return {
            "container_id": existing.short_id,
            "name": name,
            "status": existing.status,
        }
    except NotFound:
        pass

    container = client.containers.run(
        image=CONTADOR_IMAGE,
        name=name,
        detach=True,
        restart_policy={"Name": "unless-stopped", "MaximumRetryCount": 0},  # type: ignore[arg-type] # He tenido que añadir esto porque me daba un error de tipo, aunque la documentación oficial de docker-py indica que es un dict
        environment={
            "CONTADOR_ID": contador_id,
            "NUMERO_SERIE": numero_serie,
            "TIPO_SUMINISTRO": tipo_suministro,
            "BACKEND_URL": BACKEND_URL_INTERNAL,
            "INTERVALO_SEG": INTERVALO_SEG,
        },
        network=DOCKER_NETWORK,
    )

    return {
        "container_id": container.short_id,
        "name": name,
        "status": container.status,
    }


def detener_contenedor(contador_id: str) -> bool:
    """
    Para y elimina el contenedor asociado a un contador
    """
    client = _get_client()
    name = _container_name(contador_id)
    try:
        container = client.containers.get(name)
        container.stop(timeout=5)
        container.remove()
        return True
    except NotFound:
        return False
    except APIError as e:
        print(f"[docker_manager] Error al detener {name}: {e}")
        return False


def estado_contenedor(contador_id: str) -> dict | None:
    """
    Devuelve el estado del contenedor o None si no existe.
    """
    client = _get_client()
    name = _container_name(contador_id)
    try:
        c = client.containers.get(name)
        return {
            "container_id": c.short_id,
            "name": name,
            "status": c.status,
            "image": c.image.tags if c.image else [],
        }
    except NotFound:
        return None


def listar_contenedores_contadores() -> list[dict]:
    """
    Lista todos los contenedores de contadores activos.
    """
    client = _get_client()
    containers = client.containers.list(all=True, filters={"name": "contador-"})
    return [
        {
            "container_id": c.short_id,
            "name": c.name,
            "status": c.status,
        }
        for c in containers
    ]
