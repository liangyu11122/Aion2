"""bnshive (永恆蜂窩) API client — fallback data source."""
import json, time, urllib.request, urllib.parse, urllib.error

API = "https://aion-api.bnshive.com"
PROFILE_IMG = "https://profileimg.plaync.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Accept-Language": "zh-TW,zh;q=0.9",
    "Origin": "https://aion2.bnshive.com",
    "Referer": "https://aion2.bnshive.com/",
}


def _get_json(url, timeout=20):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read().decode("utf-8", "ignore") or "{}"
        return r.status, json.loads(body)


def search(keyword, server_id="", race="", page=1, size=40):
    params = {"keyword": keyword, "page": str(page), "size": str(size)}
    if server_id: params["serverId"] = str(server_id)
    if race:      params["race"]     = str(race)
    url = f"{API}/character/search?" + urllib.parse.urlencode(params)
    _, j = _get_json(url)
    return j


def query_character(server_id, character_id, max_wait_sec=25):
    """Kick off bnshive query job and poll until queryResult.data is present.

    Returns (full_json_payload, error_dict_or_None).
    """
    qs = urllib.parse.urlencode({"serverId": server_id, "characterId": character_id})
    init_url = f"{API}/character/query?{qs}"
    try:
        _, init = _get_json(init_url)
    except urllib.error.HTTPError as e:
        return None, {"error": "bnshive_query_failed", "status": e.code,
                      "body": e.read().decode("utf-8", "ignore")[:300]}
    job_id = init.get("jobId") or f"fetch:{server_id}:{character_id}"
    status_url = f"{API}/character/query/status?jobId={urllib.parse.quote(job_id)}"

    deadline = time.time() + max_wait_sec
    last = None
    while time.time() < deadline:
        try:
            _, j = _get_json(status_url)
        except urllib.error.HTTPError as e:
            return None, {"error": "bnshive_poll_failed", "status": e.code}
        last = j
        if (j.get("queryResult") or {}).get("data"):
            return j, None
        time.sleep(1.0)

    if last and (last.get("queryResult") or {}).get("data"):
        return last, None
    return None, {"error": "bnshive_timeout", "last": last}


def profile_image_raw(querystring, timeout=15):
    """Fetch a profile image; returns (status, ctype, raw_bytes)."""
    url = f"{PROFILE_IMG}/game_profile_images/aion2_tw/images?{querystring}"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.headers.get("Content-Type", "image/png"), r.read()
    except urllib.error.HTTPError as e:
        return e.code, "application/json", e.read()
