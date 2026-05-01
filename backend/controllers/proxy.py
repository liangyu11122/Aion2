"""Transparent proxies (NC API + profile images)."""
from flask import Blueprint, request, Response

from services import nc_client, bnshive_client

bp = Blueprint("proxy", __name__)


@bp.get("/proxy/ncsoft/<path:upstream>")
def proxy_nc(upstream):
    qs = request.query_string.decode("utf-8")
    full = upstream + ("?" + qs if qs else "")
    status, ctype, body = nc_client.get_raw(full)
    return Response(body, status=status, mimetype=ctype.split(";")[0])


@bp.get("/proxy/profile-img")
def proxy_profile_img():
    qs = request.query_string.decode("utf-8")
    status, ctype, body = bnshive_client.profile_image_raw(qs)
    return Response(body, status=status, mimetype=ctype.split(";")[0])
