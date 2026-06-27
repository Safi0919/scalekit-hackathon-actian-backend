import time
from functools import wraps

import jwt
import requests
from jwt.algorithms import RSAAlgorithm
from flask import g, request, current_app

# Module-level JWKS cache: { jwks_uri: {"keys": {kid: public_key}, "fetched_at": float} }
_jwks_cache: dict = {}


def _fetch_jwks(jwks_uri: str, force_refresh: bool = False) -> dict:
    """
    Return a {kid: RSA public key} dict, cached for JWKS_CACHE_TTL seconds.
    Set force_refresh=True to bypass the cache (e.g. after a key-not-found error).
    """
    ttl = current_app.config.get("JWKS_CACHE_TTL", 600)
    cached = _jwks_cache.get(jwks_uri)

    if not force_refresh and cached:
        if time.time() - cached["fetched_at"] < ttl:
            return cached["keys"]

    resp = requests.get(jwks_uri, timeout=5)
    resp.raise_for_status()

    keys = {
        entry["kid"]: RSAAlgorithm.from_jwk(entry)
        for entry in resp.json().get("keys", [])
        if "kid" in entry
    }
    _jwks_cache[jwks_uri] = {"keys": keys, "fetched_at": time.time()}
    return keys


def _resolve_public_key(token: str):
    """
    Read the 'kid' from the JWT header and look it up in JWKS.
    Retries once with a forced cache refresh to handle key rotation.
    Raises jwt.InvalidKeyError if the kid cannot be resolved.
    """
    jwks_uri = current_app.config["SCALEKIT_JWKS_URI"]
    kid = jwt.get_unverified_header(token).get("kid")

    keys = _fetch_jwks(jwks_uri)
    public_key = keys.get(kid)

    if public_key is None:
        # Key may have been rotated since the cache was last populated
        keys = _fetch_jwks(jwks_uri, force_refresh=True)
        public_key = keys.get(kid)

    if public_key is None:
        raise jwt.InvalidKeyError(f"No JWKS key found for kid={kid!r}")

    return public_key


def validate_jwt(f):
    """
    Route decorator that validates the Bearer JWT on every request.
    On success:  sets g.jwt_claims and g.created_by, then calls the route.
    On failure:  returns a JSON error response with an appropriate HTTP status.

    Security contract: fails closed — if the JWKS endpoint is unreachable the
    request is denied (503) rather than allowed through with an unverified token.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return {"data": None, "error": "Missing or malformed Authorization header"}, 401

        token = auth_header[len("Bearer "):]

        try:
            public_key = _resolve_public_key(token)

            audience = current_app.config.get("SCALEKIT_AUDIENCE") or None
            decode_options = {
                "verify_exp": True,
                "verify_nbf": True,
                "verify_iss": True,
                "verify_aud": audience is not None,
            }

            claims = jwt.decode(
                token,
                key=public_key,
                algorithms=[current_app.config.get("JWT_ALGORITHM", "RS256")],
                issuer=current_app.config["SCALEKIT_ISSUER"],
                audience=audience,
                options=decode_options,
            )

        except jwt.ExpiredSignatureError:
            return {"data": None, "error": "Token has expired"}, 401
        except jwt.InvalidAudienceError:
            return {"data": None, "error": "Invalid token audience"}, 401
        except jwt.InvalidIssuerError:
            return {"data": None, "error": "Invalid token issuer"}, 401
        except jwt.InvalidKeyError as exc:
            return {"data": None, "error": f"Token key error: {exc}"}, 401
        except jwt.PyJWTError as exc:
            return {"data": None, "error": f"Token validation failed: {exc}"}, 401
        except requests.RequestException:
            # JWKS endpoint unreachable — fail closed
            return {"data": None, "error": "Unable to verify token: JWKS endpoint unavailable"}, 503

        # Scalekit M2M tokens use client_id; user tokens fall back to sub
        g.jwt_claims = claims
        g.created_by = claims.get("client_id") or claims.get("sub") or "unknown"

        return f(*args, **kwargs)

    return decorated
