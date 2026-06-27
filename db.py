import requests

_base_url: str = ""


def get_base_url() -> str:
    if not _base_url:
        raise RuntimeError("DB not initialised — call init_db(app) first")
    return _base_url


def init_db(app) -> None:
    global _base_url
    host = app.config["VECTORAI_HOST"]
    # Use the HTTP REST port (6573), not the gRPC port (6574)
    _base_url = f"http://{host.replace(':6574', ':6573').replace(':6575', ':6573')}"

    collection = app.config["VECTORAI_COLLECTION"]
    resp = requests.get(f"{_base_url}/collections/{collection}")
    if resp.status_code == 404:
        requests.put(f"{_base_url}/collections/{collection}", json={
            "vectors": {"size": 1, "distance": "Euclid"}
        })
