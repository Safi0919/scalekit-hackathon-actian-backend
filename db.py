import requests

_base_url: str = ""


def get_base_url() -> str:
    if not _base_url:
        raise RuntimeError("DB not initialised — call init_db(app) first")
    return _base_url


def ensure_collection(collection: str) -> None:
    check_url  = f"{_base_url}/collections/{collection}"
    create_url = f"{_base_url}/collections/{collection}"

    # Check if collection exists
    check = requests.get(check_url, timeout=5)
    print(f"[DB] GET {check_url} -> {check.status_code} | {check.text[:300]}", flush=True)

    if check.status_code != 200:
        # Create the collection
        body = {"vectors": {"size": 1, "distance": "Euclid"}}
        create = requests.put(create_url, json=body, timeout=5)
        print(f"[DB] PUT {create_url} -> {create.status_code} | {create.text[:300]}", flush=True)
        if create.status_code not in (200, 201):
            raise RuntimeError(f"Failed to create collection: {create.status_code} {create.text}")


def init_db(app) -> None:
    global _base_url
    host = app.config["VECTORAI_HOST"]
    port = app.config["VECTORAI_PORT"]
    _base_url = f"http://{host}:{port}"
    print(f"[DB] VectorAI base URL: {_base_url}", flush=True)
