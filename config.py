import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    VECTORAI_HOST       = os.environ.get("VECTORAI_HOST", "localhost")
    VECTORAI_PORT       = os.environ.get("VECTORAI_PORT", "6573")
    VECTORAI_COLLECTION = os.environ.get("VECTORAI_COLLECTION", "ui_removals")
