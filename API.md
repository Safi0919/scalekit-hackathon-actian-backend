# Actian Backend API

Base URL: `https://actian-backend.onrender.com`

All requests and responses use JSON. Every response follows this envelope:

```json
{ "data": <object|array|null>, "error": <string|null> }
```

---

## GET /api/ui-removals

Returns a list of all records stored in the database.

**Query parameters (all optional)**

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | integer | Max records to return (default 100, max 500) |
| `offset` | integer | Number of records to skip (default 0) |

**Example**

```bash
curl https://actian-backend.onrender.com/api/ui-removals
```

**Response**

```json
{
  "data": [
    {
      "id": 1782601318018711,
      "change": "removed help button",
      "page": "dashboard",
      "created_at": "2026-06-27T23:01:58.018692+00:00",
      "updated_at": "2026-06-27T23:01:58.018692+00:00"
    }
  ],
  "error": null
}
```

---

## GET /api/ui-removals/<id>

Returns a single record by its ID.

**Example**

```bash
curl https://actian-backend.onrender.com/api/ui-removals/1782601318018711
```

**Response**

```json
{
  "data": {
    "id": 1782601318018711,
    "change": "removed help button",
    "page": "dashboard",
    "created_at": "2026-06-27T23:01:58.018692+00:00",
    "updated_at": "2026-06-27T23:01:58.018692+00:00"
  },
  "error": null
}
```

Returns `404` if the record does not exist.

---

## POST /api/ui-removals

Creates a new record. Accepts any JSON body — there are no mandatory fields. Send whatever data is relevant to the change being recorded.

The API automatically adds `id`, `created_at`, and `updated_at` to every record.

**Example**

```bash
curl -X POST https://actian-backend.onrender.com/api/ui-removals \
  -H "Content-Type: application/json" \
  -d '{"change": "removed help button", "page": "dashboard", "click_count": 3}'
```

**Response** — `201 Created`

```json
{
  "data": {
    "id": 1782601318018711,
    "change": "removed help button",
    "page": "dashboard",
    "click_count": 3,
    "created_at": "2026-06-27T23:01:58.018692+00:00",
    "updated_at": "2026-06-27T23:01:58.018692+00:00"
  },
  "error": null
}
```

---

## PUT /api/ui-removals/<id>

Updates an existing record. Send only the fields you want to change — all other fields remain untouched. `updated_at` is automatically bumped.

**Example**

```bash
curl -X PUT https://actian-backend.onrender.com/api/ui-removals/1782601318018711 \
  -H "Content-Type: application/json" \
  -d '{"click_count": 10, "status": "reviewed"}'
```

**Response**

```json
{
  "data": {
    "id": 1782601318018711,
    "change": "removed help button",
    "page": "dashboard",
    "click_count": 10,
    "status": "reviewed",
    "created_at": "2026-06-27T23:01:58.018692+00:00",
    "updated_at": "2026-06-27T23:05:00.000000+00:00"
  },
  "error": null
}
```

Returns `404` if the record does not exist.

---

## Error responses

| Status | Meaning |
|--------|---------|
| `400` | Bad request — missing or invalid body |
| `404` | Record not found |
| `500` | Database error |
