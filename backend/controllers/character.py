"""GET /api/char — local SQLite cache layer fronted by bnshive."""
import time, urllib.parse
from flask import Blueprint, request, jsonify

from models import character_cache
from services.bnshive_client import query_character

bp = Blueprint("character", __name__)


def _decode_repeated(s, rounds=3):
    """NC returns characterId already URL-encoded. Decode until stable."""
    for _ in range(rounds):
        if "%" not in s:
            return s
        try:
            d = urllib.parse.unquote(s)
        except Exception:
            return s
        if d == s:
            return s
        s = d
    return s


@bp.get("/api/char")
def get_character():
    sid_raw = request.args.get("serverId", "")
    cid = request.args.get("characterId", "")
    if not cid:
        return jsonify({"error": "missing_characterId"}), 400
    try:
        sid = int(sid_raw)
    except ValueError:
        return jsonify({"error": "bad_serverId"}), 400

    cid = _decode_repeated(cid)
    refresh = request.args.get("refresh") == "1"

    now = int(time.time())
    cached = character_cache.get(sid, cid)
    if cached and not refresh and now - cached["fetchedAt"] < character_cache.TTL_SEC:
        return jsonify({
            "cached": True,
            "ageSeconds": now - cached["fetchedAt"],
            "source": cached["source"],
            **cached["data"],
        })

    fresh, err = query_character(sid, cid)
    if err:
        if cached:  # fall back to stale data
            return jsonify({
                "cached": True, "stale": True,
                "ageSeconds": now - cached["fetchedAt"],
                "source": cached["source"],
                "fetchError": err,
                **cached["data"],
            })
        return jsonify({"error": "fetch_failed", **err}), 502

    character_cache.put(sid, cid, "bnshive", fresh)
    return jsonify({"cached": False, "ageSeconds": 0,
                    "source": "bnshive", **fresh})
