import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    VECTORAI_HOST       = os.environ.get("VECTORAI_HOST", "localhost:6574")
    VECTORAI_COLLECTION = os.environ.get("VECTORAI_COLLECTION", "ui_removals")
