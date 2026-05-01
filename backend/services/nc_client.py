"""NCSoft TW Aion 2 API client."""
import json, urllib.request, urllib.parse, urllib.error

BASE = "https://tw.ncsoft.com/aion2"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Accept-Language": "zh-TW",
    "Referer": "https://tw.ncsoft.com/aion2/characters/index",
}


def _get_json(url, timeout=15):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read().decode("utf-8", "ignore") or "{}"
        return r.status, json.loads(body)


def get_raw(path, timeout=20):
    """Transparent proxy: returns (status, ctype, raw_bytes) for /proxy/ncsoft/*."""
    url = f"{BASE}/{path}"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.headers.get("Content-Type", "application/octet-stream"), r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Content-Type", "application/json"), e.read()


def search(keyword, server_id="", race="", pc_id="", page=1, size=40):
    params = {"keyword": keyword, "page": str(page), "size": str(size)}
    if server_id: params["serverId"] = str(server_id)
    if race:      params["race"]     = str(race)
    if pc_id:     params["pcId"]     = str(pc_id)
    url = f"{BASE}/api/search/aion2tw/search/v2/character?" + urllib.parse.urlencode(params)
    _, j = _get_json(url)
    return j
