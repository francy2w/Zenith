from flask import Flask, request, jsonify, send_file, render_template
import sqlite3, json, secrets, base64, hashlib, os, zlib
from datetime import datetime, timedelta

app = Flask(__name__)
PORT = int(os.environ.get("PORT", 5000))

# ================= SECURITY CONFIG =================
APP_SECRET = hashlib.sha256(b"ZENITH_INTERNAL_SECRET").hexdigest()
MIN_CODE_LEN = 15

# ================= DATABASE =================
class ZenithDatabase:
    def __init__(self):
        self.conn = sqlite3.connect("zenith.db", check_same_thread=False)
        self.init_db()

    def init_db(self):
        c = self.conn.cursor()

        c.execute("""
        CREATE TABLE IF NOT EXISTS keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE,
            key_type TEXT,
            days INTEGER,
            status TEXT DEFAULT 'active',
            created_at TEXT,
            expires_at TEXT,
            discord_id TEXT,
            note TEXT
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS config (
            kill_switch INTEGER DEFAULT 0
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS loadstrings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            loadstring_id TEXT,
            encrypted_code TEXT,
            access_key TEXT,
            checksum TEXT
        )
        """)

        self.conn.commit()

    # ================= KEYS =================
    def generate_keys(self, amount, key_type, days=None):
        out = []
        c = self.conn.cursor()

        for _ in range(amount):
            key = "ZENITH-" + secrets.token_hex(8).upper()
            expires = None

            if key_type == "day":
                expires = (datetime.utcnow() + timedelta(days=days)).isoformat()

            c.execute("""
            INSERT INTO keys (key, key_type, days, created_at, expires_at)
            VALUES (?, ?, ?, ?, ?)
            """, (key, key_type, days, datetime.utcnow().isoformat(), expires))

            out.append(key)

        self.conn.commit()
        return out

    def check_key(self, key):
        c = self.conn.cursor()
        c.execute("SELECT * FROM keys WHERE key=?", (key,))
        k = c.fetchone()

        if not k:
            return {"valid": False, "error": "Key not found"}

        c.execute("SELECT kill_switch FROM config LIMIT 1")
        ks = c.fetchone()

        if ks and ks[0] == 1:
            return {"valid": False, "error": "System disabled"}

        if k[6] and datetime.utcnow() > datetime.fromisoformat(k[6]):
            return {"valid": False, "error": "Key expired"}

        return {
            "valid": True,
            "type": k[2],
            "expires_at": k[6]
        }

    def stats(self):
        c = self.conn.cursor()
        return {
            "total": c.execute("SELECT COUNT(*) FROM keys").fetchone()[0],
            "active": c.execute("SELECT COUNT(*) FROM keys WHERE status='active'").fetchone()[0],
            "loadstrings": c.execute("SELECT COUNT(*) FROM loadstrings").fetchone()[0]
        }

    def toggle_kill(self, v):
        c = self.conn.cursor()
        c.execute("DELETE FROM config")
        c.execute("INSERT INTO config VALUES (?)", (1 if v else 0,))
        self.conn.commit()

    def export(self, fmt):
        c = self.conn.cursor()
        c.execute("SELECT key,key_type,expires_at FROM keys")
        data = c.fetchall()

        if fmt == "json":
            return json.dumps([
                {"key":k[0],"type":k[1],"expires":k[2]} for k in data
            ], indent=2)

        if fmt == "csv":
            return "key,type,expires\n" + "\n".join(
                f"{k[0]},{k[1]},{k[2]}" for k in data
            )

        return "\n".join(
            f"{k[0]} | {k[1]} | {k[2] or 'Lifetime'}" for k in data
        )

    # ================= LOADSTRING =================
    def create_loadstring(self, code):
        access_key = secrets.token_hex(24)
        checksum = hashlib.sha256(code.encode()).hexdigest()

        compressed = zlib.compress(code.encode())
        enc = base64.b64encode(compressed).decode()[::-1]

        ls_id = "LS" + secrets.token_hex(10)

        c = self.conn.cursor()
        c.execute("""
        INSERT INTO loadstrings (loadstring_id, encrypted_code, access_key, checksum)
        VALUES (?, ?, ?, ?)
        """, (ls_id, enc, access_key, checksum))

        self.conn.commit()

        lua_loader = f'''
-- obfuscated by Zenith --
-- much love Francy ❤️

_G.ZenithAccessKey = "{access_key}"

local function _zx(a)
    local b = a:reverse()
    local c = game:GetService("HttpService"):Base64Decode(b)
    return c
end

local function _chk(d)
    return d and #d > 10
end

local raw = _zx("{enc}")

if _G.ZenithAccessKey ~= "{access_key}" then
    error("Invalid access key")
end

if not _chk(raw) then
    error("Corrupted payload")
end

local ok, decoded = pcall(function()
    return game:GetService("HttpService"):JSONDecode(
        game:GetService("HttpService"):JSONEncode(raw)
    )
end)

local z = raw
local f = loadstring(z)

if not f then
    error("Execution blocked")
end

return f()
'''

        return {
            "success": True,
            "loadstring_id": ls_id,
            "access_key": access_key,
            "loadstring_code": lua_loader
        }

db = ZenithDatabase()

# ================= OBFUSCATOR (MULTI-LAYER) =================
def heavy_obfuscate(code):
    # Layer 1 – checksum
    checksum = hashlib.sha256(code.encode()).hexdigest()

    # Layer 2 – compress
    compressed = zlib.compress(code.encode())

    # Layer 3 – base64
    b64 = base64.b64encode(compressed).decode()

    # Layer 4 – reverse
    rev = b64[::-1]

    # Layer 5 – fake noise
    noise = secrets.token_hex(12)

    return f'''
-- obfuscated by Zenith --
-- much love Francy ❤️

local _n="{noise}"
local _d="{rev}"
local _h="{checksum}"

local function _r(s)
    return s:reverse()
end

local function _b(s)
    return game:GetService("HttpService"):Base64Decode(s)
end

local raw = _b(_r(_d))

if #raw < 10 then
    error("Payload damaged")
end

local f = loadstring(raw)
if not f then
    error("Execution failed")
end

return f()
'''

# ================= ROUTES =================
@app.route("/")
def index():
    return render_template("index.html", port=PORT)

@app.route("/api/stats")
def stats():
    return jsonify(db.stats())

@app.route("/api/generate", methods=["POST"])
def generate():
    d = request.json
    return jsonify({
        "success": True,
        "keys": db.generate_keys(
            int(d.get("amount",1)),
            d.get("type","lifetime"),
            int(d.get("days",0)) if d.get("type")=="day" else None
        )
    })

@app.route("/api/check/<key>")
def check(key):
    return jsonify(db.check_key(key))

@app.route("/api/killswitch/<v>")
def kill(v):
    db.toggle_kill(v in ("enable","on"))
    return jsonify({"success": True})

@app.route("/api/export/<fmt>")
def export(fmt):
    f = db.export(fmt)
    name = f"keys.{fmt}"
    open(name,"w").write(f)
    return send_file(name, as_attachment=True)

@app.route("/api/obfuscate", methods=["POST"])
def obf():
    code = request.json.get("code","")
    if len(code) < MIN_CODE_LEN:
        return jsonify({"success": False, "error": "Code too short"})
    return jsonify({"success": True, "obfuscated": heavy_obfuscate(code)})

@app.route("/api/loadstring/create", methods=["POST"])
def ls_create():
    code = request.json.get("code","")
    if len(code) < MIN_CODE_LEN:
        return jsonify({"success": False, "error": "Code too short"})
    return jsonify(db.create_loadstring(code))

# ================= GUNICORN ENTRY =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
