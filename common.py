"""Shared helpers: settings, the CSV files, state.json and the BookStack API."""
import csv, json, mimetypes, os, urllib.parse, urllib.request, uuid

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "state.json")


def settings():
    """Environment variables, with .env next to the scripts filling any gaps."""
    env = {}
    path = os.path.join(HERE, ".env")
    if os.path.exists(path):
        for line in open(path, encoding="utf8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    env.update({k: v for k, v in os.environ.items() if k.startswith("BOOKSTACK_")})
    return env


def read_csv(name):
    path = os.path.join(HERE, name)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf8", newline="") as f:
        lines = [l for l in f if l.strip() and not l.lstrip().startswith("#")]
    return list(csv.DictReader(lines, delimiter="|"))


def pages():
    """pages.csv: page_id|icon|from|to|title|subtitle"""
    return {r["page_id"].strip(): r for r in read_csv("pages.csv")}


def books():
    """books.csv: target|icon|from|to|bright|title|subtitle (target = books/<slug> or shelves/<slug>)"""
    return {r["target"].strip(): r for r in read_csv("books.csv")}


def load_state():
    return json.load(open(STATE, encoding="utf8")) if os.path.exists(STATE) else {"pages": {}, "books": {}}


def save_state(state):
    with open(STATE, "w", encoding="utf8") as f:
        json.dump(state, f, indent=1)


def versioned(entry, key):
    """'/uploads/.../banner-p12.png?v=3' (the version busts browser caches after a re-upload)"""
    return f'{entry[key]}?v={entry.get(key + "_v", 1)}'


class API:
    def __init__(self):
        cfg = settings()
        missing = [k for k in ("BOOKSTACK_URL", "BOOKSTACK_TOKEN_ID", "BOOKSTACK_TOKEN_SECRET") if not cfg.get(k)]
        if missing:
            raise SystemExit("Missing in .env: " + ", ".join(missing) + " (see .env.example)")
        self.base = cfg["BOOKSTACK_URL"].rstrip("/") + "/api/"
        self.auth = f'Token {cfg["BOOKSTACK_TOKEN_ID"]}:{cfg["BOOKSTACK_TOKEN_SECRET"]}'

    def call(self, method, path, data=None, files=None):
        headers = {"Authorization": self.auth, "Accept": "application/json"}
        body = None
        if files:
            body, ctype = _multipart(data or {}, files)
            headers["Content-Type"] = ctype
        elif data is not None:
            body = json.dumps(data).encode()
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(self.base + path, body, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            raise SystemExit(f"{method} /api/{path} failed: {e.code} {e.read().decode(errors='replace')[:300]}")

    def listing(self, kind):
        out, offset = [], 0
        while True:
            d = self.call("GET", f"{kind}?count=500&offset={offset}")
            out += d["data"]
            offset += len(d["data"])
            if not d["data"] or offset >= d["total"]:
                return out


def _multipart(fields, files):
    boundary = uuid.uuid4().hex
    parts = []
    for k, v in fields.items():
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    for k, path in files.items():
        name = os.path.basename(path)
        ctype = mimetypes.guess_type(name)[0] or "application/octet-stream"
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"; filename="{name}"\r\n'
                     f'Content-Type: {ctype}\r\n\r\n'.encode() + open(path, "rb").read() + b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def url_path(url):
    """BookStack returns absolute image URLs; keep only the path so the site works under any hostname."""
    return urllib.parse.urlparse(url).path
