from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional


@dataclass
class UIRemoval:
    id: int
    element_id: str
    page_url: str
    click_count: int
    removed_at: datetime
    metadata: str
    created_by: str
    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> dict:
        d = asdict(self)
        for key in ("removed_at", "created_at", "updated_at"):
            if isinstance(d[key], datetime):
                d[key] = d[key].isoformat()
        return d


@dataclass
class UIRemovalCreate:
    element_id: str
    page_url: str
    click_count: int
    removed_at: Optional[str] = None
    metadata: Optional[str] = None
    created_by: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "UIRemovalCreate":
        missing = [f for f in ("element_id", "page_url", "click_count") if not data.get(f) and data.get(f) != 0]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
        return cls(
            element_id=str(data["element_id"]),
            page_url=str(data["page_url"]),
            click_count=int(data["click_count"]),
            removed_at=data.get("removed_at"),
            metadata=data.get("metadata"),
            created_by=data.get("created_by"),
        )


@dataclass
class UIRemovalUpdate:
    element_id: Optional[str] = None
    page_url: Optional[str] = None
    click_count: Optional[int] = None
    removed_at: Optional[str] = None
    metadata: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "UIRemovalUpdate":
        return cls(
            element_id=data.get("element_id"),
            page_url=data.get("page_url"),
            click_count=int(data["click_count"]) if "click_count" in data else None,
            removed_at=data.get("removed_at"),
            metadata=data.get("metadata"),
        )
