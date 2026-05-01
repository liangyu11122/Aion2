"""Search orchestration: NC official → bnshive fallback.

Returns a normalised shape so the front-end doesn't care which source won.
"""
from . import nc_client, bnshive_client


def _normalise_bnshive(results, pc_id_filter=""):
    out = []
    for r in results:
        if pc_id_filter and r.get("pcId") and str(r.get("pcId")) != str(pc_id_filter):
            continue
        prof = r.get("profileImageUrl") or ""
        # Strip absolute prefix so the SPA can hit /proxy/profile-img
        if prof.startswith("http") and "/game_profile_images/" in prof:
            prof = "/" + prof.split("/", 3)[-1]
        out.append({
            "name": r.get("characterName") or "",
            "characterId": r.get("characterId"),
            "serverId": r.get("serverId"),
            "serverName": r.get("serverName") or "",
            "level": r.get("characterLevel"),
            "race": r.get("raceId"),
            "pcId": r.get("pcId"),
            "profileImageUrl": prof,
        })
    return out


def search(keyword, server_id="", race="", pc_id="", page=1, size=40):
    nc_err = None
    try:
        nc_j = nc_client.search(keyword, server_id, race, pc_id, page, size)
        nc_list = nc_j.get("list") or []
        if nc_list:
            return {
                "source": "nc",
                "list": nc_list,
                "total": (nc_j.get("pagination") or {}).get("total", len(nc_list)),
            }
        nc_err = "empty"
    except Exception as e:
        nc_err = str(e)

    try:
        bn_j = bnshive_client.search(keyword, server_id, race, page, size)
    except Exception as e:
        return {"source": "none", "list": [], "total": 0,
                "ncError": nc_err, "bnshiveError": str(e)}

    normalised = _normalise_bnshive(bn_j.get("results") or [], pc_id)
    return {
        "source": "bnshive",
        "list": normalised,
        "total": bn_j.get("total", len(normalised)),
        "ncError": nc_err,
    }
