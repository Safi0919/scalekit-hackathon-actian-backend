import requests
import logging

logger = logging.getLogger(__name__)

_base_url: str = ""


def get_base_url() -> str:
    if not _base_url:
        raise RuntimeError("DB not initialised — call init_db(app) first")
    return _base_url


def ensure_collection(collection: str) -> None:
    try:
        resp = requests.get(f"{_base_url}/collections/{collection}", timeout=5)
        if resp.status_code == 404:
            requests.put(f"{_base_url}/collections/{collection}", json={
                "vectors": {"size": 1, "distance": "Euclid"}
            }, timeout=5)
    except Exception as exc:
        logger.error("Could not connect to VectorAI: %s", exc)
        raise


def init_db(app) -> None:
    global _base_url
    host = app.config["VECTORAI_HOST"]
    port = app.config["VECTORAI_PORT"]
    _base_url = f"http://{host}:{port}"
    logger.info("VectorAI base URL: %s", _base_url)
