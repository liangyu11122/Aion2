"""GET /api/search — character search (NC → bnshive fallback)."""
from flask import Blueprint, request, jsonify

from services.search_service import search as svc_search

bp = Blueprint("search", __name__)


@bp.get("/api/search")
def search():
    keyword = (request.args.get("keyword") or "").strip()
    if not keyword:
        return jsonify({"error": "missing_keyword"}), 400
    try:
        page = int(request.args.get("page") or 1)
        size = int(request.args.get("size") or 40)
    except ValueError:
        return jsonify({"error": "bad_pagination"}), 400
    return jsonify(svc_search(
        keyword=keyword,
        server_id=request.args.get("serverId") or "",
        race=request.args.get("race") or "",
        pc_id=request.args.get("pcId") or "",
        page=page, size=size,
    ))
