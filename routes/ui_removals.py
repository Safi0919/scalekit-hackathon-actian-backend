import time
from datetime import datetime, timezone

import requests
from flask import Blueprint, current_app, jsonify, request

from db import get_base_url, ensure_collection

ui_removals_bp = Blueprint("ui_removals", __name__)

_DUMMY_VEC = [0.0]


def _collection_url() -> str:
    collection = current_app.config["VECTORAI_COLLECTION"]
    ensure_collection(collection)
    return f"{get_base_url()}/collections/{collection}/points"


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
        resp = requests.post(f"{_collection_url()}/scroll", json={
            "limit": 5000,
            "with_payload": True,
            "with_vector": False,
        })
        resp.raise_for_status()
        points = resp.json().get("result", {}).get("points", [])
    except Exception as exc:
        current_app.logger.error("VectorAI error in list_ui_removals: %s", exc)
        return _err("Database error", 500)

    results = [{"id": p["id"], **p["payload"]} for p in points]
    results.sort(key=lambda r: r.get("created_at", ""), reverse=True)
    return _ok(results[offset: offset + limit])


# ── GET /api/ui-removals/<id> ─────────────────────────────────────────────────

@ui_removals_bp.route("/ui-removals/<int:record_id>", methods=["GET"])
def get_ui_removal(record_id: int):
    try:
        resp = requests.get(f"{_collection_url()}/{record_id}")
    except Exception as exc:
        current_app.logger.error("VectorAI error in get_ui_removal: %s", exc)
        return _err("Database error", 500)

    if resp.status_code == 404:
        return _err("Record not found", 404)

    resp.raise_for_status()
    point = resp.json().get("result", {})
    return _ok({"id": point["id"], **point["payload"]})


# ── POST /api/ui-removals ─────────────────────────────────────────────────────

@ui_removals_bp.route("/ui-removals", methods=["POST"])
def create_ui_removal():
    body = request.get_json(silent=True)
    if not body:
        return _err("Request body must be JSON")

    now       = datetime.now(timezone.utc).isoformat()
    record_id = int(time.time() * 1_000_000)

    payload = {**body, "created_at": now, "updated_at": now}

    try:
        resp = requests.put(_collection_url(), json={
            "points": [{"id": record_id, "vector": _DUMMY_VEC, "payload": payload}]
        })
        resp.raise_for_status()
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

    # Fetch existing point
    try:
        resp = requests.get(f"{_collection_url()}/{record_id}")
    except Exception as exc:
        current_app.logger.error("VectorAI error in update_ui_removal (get): %s", exc)
        return _err("Database error", 500)

    if resp.status_code == 404:
        return _err("Record not found", 404)

    existing_payload = resp.json().get("result", {}).get("payload", {})

    merged = {
        **existing_payload,
        **body,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        resp = requests.put(_collection_url(), json={
            "points": [{"id": record_id, "vector": _DUMMY_VEC, "payload": merged}]
        })
        resp.raise_for_status()
    except Exception as exc:
        current_app.logger.error("VectorAI error in update_ui_removal (upsert): %s", exc)
        return _err("Database error", 500)

    return _ok({"id": record_id, **merged})
