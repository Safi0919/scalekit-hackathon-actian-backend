from actian_vectorai import VectorAIClient, VectorParams, Distance, CollectionExistsError

# Module-level singleton — VectorAI client is thread-safe and long-lived
_client: VectorAIClient | None = None


def get_client() -> VectorAIClient:
    if _client is None:
        raise RuntimeError("VectorAI client not initialised — call init_db(app) first")
    return _client


def init_db(app) -> None:
    """
    Called once from the app factory.
    Creates the VectorAI client and ensures the collection exists.
    Uses a 1-dimensional dummy vector (Euclid distance) because this project
    uses VectorAI as a document store, not for semantic search.
    """
    global _client
    _client = VectorAIClient(app.config["VECTORAI_HOST"])
    _client.connect()

    try:
        _client.collections.create(
            app.config["VECTORAI_COLLECTION"],
            vectors_config=VectorParams(size=1, distance=Distance.Euclid),
        )
    except CollectionExistsError:
        pass
