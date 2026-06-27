import time
from datetime import datetime, timezone

from actian_vectorai import PointStruct
from flask import Blueprint, current_app, jsonify, request

from db import get_client

ui_removals_bp = Blueprint("ui_removals", __name__)

_DUMMY_VEC = [0.0]


def _point_to_dict(point) -> dict:
    d = dict(point.payload)
    d["id"] = point.id
    return d


def _ok(data, status: int = 200):
    return jsonify({"data": data, "error": None}), status


def _err(message: str, status: int = 400):
    return jsonify({"data": None, "error": message}), status


# ── GET /api/ui-removals ──────────────────────────────────────────────────────

@ui_removals_bp.route("/ui-removals", methods=["GET"])
def list_ui_removals():
    try:
        limit  = min(int(request.args.get("limit",  100)), 500)
        offset = max(int(request.args.get("offset",   0)),   0)
    except ValueError:
        return _err("limit and offset must be integers")

    try:
        records, _ = get_client().points.scroll(
            current_app.config["VECTORAI_COLLECTION"],
            limit=5000,
            with_payload=True,
            with_vectors=False,
        )
    except Exception as exc:
        current_app.logger.error("VectorAI error in list_ui_removals: %s", exc)
        return _err("Database error", 500)

    results = [_point_to_dict(r) for r in records]
    return _ok(results[offset: offset + limit])


# ── GET /api/ui-removals/<id> ─────────────────────────────────────────────────

@ui_removals_bp.route("/ui-removals/<int:record_id>", methods=["GET"])
def get_ui_removal(record_id: int):
    try:
        records = get_client().points.get(
            current_app.config["VECTORAI_COLLECTION"],
            ids=[record_id],
            with_payload=True,
            with_vectors=False,
        )
    except Exception as exc:
        current_app.logger.error("VectorAI error in get_ui_removal: %s", exc)
        return _err("Database error", 500)

    if not records:
        return _err("Record not found", 404)

    return _ok(_point_to_dict(records[0]))


# ── POST /api/ui-removals ─────────────────────────────────────────────────────

@ui_removals_bp.route("/ui-removals", methods=["POST"])
def create_ui_removal():
    body = request.get_json(silent=True)
    if not body:
        return _err("Request body must be JSON")

    now       = datetime.now(timezone.utc).isoformat()
    record_id = int(time.time() * 1_000_000)

    # Store whatever the caller sends, plus auto-add id/timestamps
    payload = {
        **body,
        "created_at": now,
        "updated_at": now,
    }

    try:
        get_client().points.upsert(
            current_app.config["VECTORAI_COLLECTION"],
            [PointStruct(id=record_id, vector=_DUMMY_VEC, payload=payload)],
        )
    except Exception as exc:
        current_app.logger.error("VectorAI error in create_ui_removal: %s", exc)
        return _err("Database error", 500)

    return _ok({"id": record_id, **payload}, 201)


# ── PUT /api/ui-removals/<id> ─────────────────────────────────────────────────

@ui_removals_bp.route("/ui-removals/<int:record_id>", methods=["PUT"])
def update_ui_removal(record_id: int):
    body = request.get_json(silent=True)
    if not body:
        return _err("Request body must be JSON")

    client     = get_client()
    collection = current_app.config["VECTORAI_COLLECTION"]

    try:
        existing = client.points.get(
            collection,
            ids=[record_id],
            with_payload=True,
            with_vectors=False,
        )
    except Exception as exc:
        current_app.logger.error("VectorAI error in update_ui_removal (get): %s", exc)
        return _err("Database error", 500)

    if not existing:
        return _err("Record not found", 404)

    # Merge whatever fields the caller provides into the existing payload
    merged = {
        **existing[0].payload,
        **body,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        client.points.upsert(
            collection,
            [PointStruct(id=record_id, vector=_DUMMY_VEC, payload=merged)],
        )
    except Exception as exc:
        current_app.logger.error("VectorAI error in update_ui_removal (upsert): %s", exc)
        return _err("Database error", 500)

    return _ok({"id": record_id, **merged})
