"""
Aion 2 local site server.

- Serves static files from the script's folder (index.html, etc.)
- /proxy/ncsoft/<path>  -> https://tw.ncsoft.com/aion2/<path>
- /proxy/profile-img?... -> https://profileimg.plaync.com/...
- /api/char?serverId=&characterId=&refresh=0|1
    Local SQLite cache layer. On cache miss (or refresh=1), queries the
    bnshive backend (https://aion-api.bnshive.com), polls until ready,
    stores result locally, returns JSON.

Run:
    python server.py            # default http://127.0.0.1:5180
    python server.py 8080       # custom port
"""
import sys, os, json, time, sqlite3, threading
import urllib.request, urllib.parse, urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5180

NC_BASE = "https://tw.ncsoft.com/aion2"
PROFILE_IMG_BASE = "https://profileimg.plaync.com"
BNSHIVE_API = "https://aion-api.bnshive.com"

CACHE_DB = os.path.join(ROOT, "char_cache.sqlite")
CACHE_TTL_SEC = 3600  # 1 hour

UPSTREAM_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Accept-Language": "zh-TW",
    "Referer": "https://tw.ncsoft.com/aion2/characters/index",
}
BNSHIVE_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Accept-Language": "zh-TW,zh;q=0.9",
    "Origin": "https://aion2.bnshive.com",
    "Referer": "https://aion2.bnshive.com/",
}


# ---------- SQLite cache ----------
_db_lock = threading.Lock()

def _db():
    conn = sqlite3.connect(CACHE_DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS characters(
        server_id   INTEGER NOT NULL,
        character_id TEXT  NOT NULL,
        fetched_at  INTEGER NOT NULL,
        source      TEXT,
        data_json   TEXT NOT NULL,
        PRIMARY KEY(server_id, character_id))""")
    return conn

def cache_get(server_id, character_id):
    with _db_lock, _db() as c:
        row = c.execute(
            "SELECT fetched_at, source, data_json FROM characters WHERE server_id=? AND character_id=?",
            (server_id, character_id)).fetchone()
    if not row:
        return None
    return {"fetchedAt": row[0], "source": row[1], "data": json.loads(row[2])}

def cache_put(server_id, character_id, source, data):
    payload = json.dumps(data, ensure_ascii=False)
    with _db_lock, _db() as c:
        c.execute(
            "INSERT OR REPLACE INTO characters(server_id,character_id,fetched_at,source,data_json) VALUES(?,?,?,?,?)",
            (server_id, character_id, int(time.time()), source, payload))
        c.commit()


# ---------- bnshive fetch ----------
def _http_json(url, timeout=20):
    req = urllib.request.Request(url, headers=BNSHIVE_HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read().decode("utf-8", "ignore")
        return r.status, json.loads(body) if body else {}

def fetch_char_via_bnshive(server_id, character_id, max_wait_sec=25):
    """Kick off bnshive query job, then poll status until queryResult.data is present."""
    qs = urllib.parse.urlencode({"serverId": server_id, "characterId": character_id})
    init_url = f"{BNSHIVE_API}/character/query?{qs}"
    try:
        status, init = _http_json(init_url)
    except urllib.error.HTTPError as e:
        return None, {"error": "bnshive_query_failed", "status": e.code,
                      "body": e.read().decode("utf-8", "ignore")[:300]}
    job_id = init.get("jobId") or f"fetch:{server_id}:{character_id}"
    status_url = f"{BNSHIVE_API}/character/query/status?jobId={urllib.parse.quote(job_id)}"

    deadline = time.time() + max_wait_sec
    last = None
    while time.time() < deadline:
        try:
            _, j = _http_json(status_url)
        except urllib.error.HTTPError as e:
            return None, {"error": "bnshive_poll_failed", "status": e.code}
        last = j
        qr = j.get("queryResult") or {}
        if qr.get("data"):
            return j, None
        # If still pending and no data, wait
        time.sleep(1.0)
    # Return whatever we have, even if partial
    if last and (last.get("queryResult") or {}).get("data"):
        return last, None
    return None, {"error": "bnshive_timeout", "last": last}


# ---------- search with NC -> bnshive fallback ----------
def _http_get_json(url, headers, timeout=15):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, json.loads(r.read().decode("utf-8", "ignore") or "{}")

def search_chars(keyword, server_id="", race="", pc_id="", page=1, size=40):
    """Try NC search first; on failure or empty result, fall back to bnshive."""
    # ---- NC search ----
    nc_params = {"keyword": keyword, "page": str(page), "size": str(size)}
    if server_id: nc_params["serverId"] = str(server_id)
    if race:      nc_params["race"]     = str(race)
    if pc_id:     nc_params["pcId"]     = str(pc_id)
    nc_url = f"{NC_BASE}/api/search/aion2tw/search/v2/character?" + urllib.parse.urlencode(nc_params)
    nc_err = None
    try:
        _, nc_j = _http_get_json(nc_url, UPSTREAM_HEADERS)
        nc_list = nc_j.get("list") or []
        if nc_list:
            return {"source": "nc", "list": nc_list,
                    "total": (nc_j.get("pagination") or {}).get("total", len(nc_list))}
        nc_err = "empty"
    except Exception as e:
        nc_err = str(e)

    # ---- bnshive fallback ----
    bn_params = {"keyword": keyword, "page": str(page), "size": str(size)}
    if server_id: bn_params["serverId"] = str(server_id)
    if race:      bn_params["race"]     = str(race)
    bn_url = f"{BNSHIVE_API}/character/search?" + urllib.parse.urlencode(bn_params)
    try:
        _, bn_j = _http_get_json(bn_url, BNSHIVE_HEADERS)
    except Exception as e:
        return {"source": "none", "list": [], "total": 0,
                "ncError": nc_err, "bnshiveError": str(e)}
    bn_results = bn_j.get("results") or []
    # Normalise to NC shape: name, characterId, serverId, serverName, level, race, pcId, profileImageUrl
    normalised = []
    for r in bn_results:
        # Optional client-side class filter (bnshive doesn't always support it server-side)
        if pc_id and r.get("pcId") and str(r.get("pcId")) != str(pc_id):
            continue
        prof = r.get("profileImageUrl") or ""
        # bnshive sometimes returns absolute URLs - keep query string only for our proxy
        if prof.startswith("http"):
            prof = "/" + prof.split("/", 3)[-1] if "/game_profile_images/" in prof else prof
        normalised.append({
            "name": r.get("characterName") or "",
            "characterId": r.get("characterId"),
            "serverId": r.get("serverId"),
            "serverName": r.get("serverName") or "",
            "level": r.get("characterLevel"),
            "race": r.get("raceId"),
            "pcId": r.get("pcId"),
            "profileImageUrl": prof,
        })
    return {"source": "bnshive", "list": normalised,
            "total": bn_j.get("total", len(normalised)),
            "ncError": nc_err}

MIME = {
    ".html": "text/html; charset=utf-8",
    ".css":  "text/css; charset=utf-8",
    ".js":   "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg":  "image/svg+xml",
    ".png":  "image/png", ".jpg":"image/jpeg", ".jpeg":"image/jpeg",
    ".webp": "image/webp", ".ico":"image/x-icon",
}


class H(BaseHTTPRequestHandler):
    def log_message(self, fmt, *a):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % a))

    # ---------- helpers ----------
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")

    def _send(self, status, body, ctype="application/json; charset=utf-8"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False).encode("utf-8")
        elif isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    # ---------- routing ----------
    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()

    def do_GET(self):
        path = self.path
        if path.startswith("/api/char"):
            return self._char_api(path)
        if path.startswith("/api/search"):
            return self._search_api(path)
        if path.startswith("/proxy/ncsoft/"):
            return self._proxy(NC_BASE + "/" + path[len("/proxy/ncsoft/"):])
        if path.startswith("/proxy/profile-img"):
            qs = path.split("?", 1)[1] if "?" in path else ""
            return self._proxy(PROFILE_IMG_BASE +
                               "/game_profile_images/aion2_tw/images?" + qs,
                               binary=True)
        return self._static(path)

    def _search_api(self, path):
        qs = urllib.parse.parse_qs(path.split("?", 1)[1] if "?" in path else "")
        kw = qs.get("keyword", [""])[0].strip()
        if not kw:
            return self._send(400, {"error": "missing_keyword"})
        result = search_chars(
            keyword=kw,
            server_id=qs.get("serverId", [""])[0],
            race=qs.get("race", [""])[0],
            pc_id=qs.get("pcId", [""])[0],
            page=int(qs.get("page", ["1"])[0] or 1),
            size=int(qs.get("size", ["40"])[0] or 40),
        )
        return self._send(200, result)

    # ---------- character cache api ----------
    def _char_api(self, path):
        qs = urllib.parse.parse_qs(path.split("?", 1)[1] if "?" in path else "")
        try:
            sid = int(qs.get("serverId", [""])[0])
        except ValueError:
            return self._send(400, {"error": "bad_serverId"})
        cid = qs.get("characterId", [""])[0]
        if not cid:
            return self._send(400, {"error": "missing_characterId"})
        # NC returns characterId already percent-encoded; if the front-end
        # encodeURIComponent's it again we get %253D etc. Decode until stable.
        for _ in range(3):
            if "%" not in cid: break
            try:
                dec = urllib.parse.unquote(cid)
            except Exception:
                break
            if dec == cid: break
            cid = dec
        refresh = qs.get("refresh", ["0"])[0] == "1"

        cached = cache_get(sid, cid)
        now = int(time.time())
        if cached and not refresh and now - cached["fetchedAt"] < CACHE_TTL_SEC:
            return self._send(200, {
                "cached": True,
                "ageSeconds": now - cached["fetchedAt"],
                "source": cached["source"],
                **cached["data"],
            })

        # Fetch fresh from bnshive
        result, err = fetch_char_via_bnshive(sid, cid)
        if err:
            # Fall back to stale cache if available
            if cached:
                return self._send(200, {
                    "cached": True,
                    "stale": True,
                    "ageSeconds": now - cached["fetchedAt"],
                    "source": cached["source"],
                    "fetchError": err,
                    **cached["data"],
                })
            return self._send(502, {"error": "fetch_failed", **err})
        cache_put(sid, cid, "bnshive", result)
        return self._send(200, {"cached": False, "ageSeconds": 0,
                                "source": "bnshive", **result})

    # ---------- proxy ----------
    def _proxy(self, url, binary=False):
        try:
            req = urllib.request.Request(url, headers=UPSTREAM_HEADERS)
            r = urllib.request.urlopen(req, timeout=20)
            data = r.read()
            ctype = r.headers.get("Content-Type", "application/octet-stream")
            self.send_response(r.status)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self._cors()
            self.end_headers()
            self.wfile.write(data)
        except urllib.error.HTTPError as e:
            body = e.read() if not binary else b""
            try:
                payload = json.loads(body)
            except Exception:
                payload = {"upstreamStatus": e.code,
                           "upstreamBody": body.decode("utf-8", "ignore")[:300]}
            self._send(e.code, {"error": "upstream_http_error", **(payload if isinstance(payload, dict) else {"data": payload})})
        except Exception as e:
            self._send(502, {"error": "proxy_failed", "detail": str(e)})

    # ---------- static ----------
    def _static(self, path):
        if "?" in path: path = path.split("?", 1)[0]
        if path == "/" or path == "":
            path = "/index.html"
        # prevent traversal
        rel = urllib.parse.unquote(path).lstrip("/")
        full = os.path.normpath(os.path.join(ROOT, rel))
        if not full.startswith(ROOT) or not os.path.isfile(full):
            return self._send(404, {"error": "not_found", "path": path})
        ext = os.path.splitext(full)[1].lower()
        ctype = MIME.get(ext, "application/octet-stream")
        with open(full, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self._cors()
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), H)
    print(f"Aion 2 local site running at  http://127.0.0.1:{PORT}/")
    print(f"  Static root: {ROOT}")
    print(f"  Proxy:       /proxy/ncsoft/...  ->  {NC_BASE}/...")
    print(f"  Char cache:  /api/char?serverId=&characterId=  (db: {CACHE_DB})")
    print("Press Ctrl+C to stop.")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")
