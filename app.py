from flask import Flask, request, jsonify, send_file, render_template
import sqlite3, json, secrets, base64
from datetime import datetime, timedelta
import os

app = Flask(__name__)
PORT = int(os.environ.get("PORT", 5000))

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
            access_key TEXT
        )
        """)
        self.conn.commit()

    # --- Key Generation ---
    def generate_keys(self, amount, key_type, days=None):
        out = []
        c = self.conn.cursor()
        for _ in range(amount):
            key = "ZENITH-" + secrets.token_hex(8).upper()
            expires = None
            if key_type == "day":
                expires = (datetime.utcnow() + timedelta(days=days)).isoformat()
            c.execute(
                "INSERT INTO keys (key, key_type, days, created_at, expires_at) VALUES (?, ?, ?, ?, ?)",
                (key, key_type, days, datetime.utcnow().isoformat(), expires)
            )
            out.append(key)
        self.conn.commit()
        return out

    # --- Check Key ---
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

        if k[6]:
            if datetime.utcnow() > datetime.fromisoformat(k[6]):
                return {"valid": False, "error": "Key expired"}

        return {"valid": True, "type": k[2], "expires_at": k[6]}

    # --- Stats ---
    def stats(self):
        c = self.conn.cursor()
        return {
            "total": c.execute("SELECT COUNT(*) FROM keys").fetchone()[0],
            "active": c.execute("SELECT COUNT(*) FROM keys WHERE status='active'").fetchone()[0],
            "loadstrings": c.execute("SELECT COUNT(*) FROM loadstrings").fetchone()[0],
        }

    # --- Kill Switch ---
    def toggle_kill(self, v):
        c = self.conn.cursor()
        c.execute("DELETE FROM config")
        c.execute("INSERT INTO config VALUES (?)", (1 if v else 0,))
        self.conn.commit()

    # --- Export Keys ---
    def export(self, fmt):
        c = self.conn.cursor()
        c.execute("SELECT key,key_type,expires_at FROM keys")
        data = c.fetchall()
        if fmt == "json":
            return json.dumps([{"key":k[0],"type":k[1],"expires":k[2]} for k in data], indent=2)
        if fmt == "csv":
            return "key,type,expires\n" + "\n".join(f"{k[0]},{k[1]},{k[2]}" for k in data)
        return "\n".join(f"{k[0]} | {k[1]} | {k[2] or 'Lifetime'}" for k in data)

    # --- Loadstring Protection ---
    def create_loadstring(self, code):
        key = secrets.token_hex(16)
        enc = base64.b64encode(code.encode()).decode()
        ls_id = "LS" + secrets.token_hex(10)
        c = self.conn.cursor()
        c.execute(
            "INSERT INTO loadstrings (loadstring_id, encrypted_code, access_key) VALUES (?,?,?)",
            (ls_id, enc, key)
        )
        self.conn.commit()
        loadstring_code = f"""-- Zenith Protected Loadstring
_G.ZenithAccessKey="{key}"
local enc="{enc}"
local decoded=game:GetService("HttpService"):Base64Decode(enc)
if _G.ZenithAccessKey=="{key}" then
    loadstring(decoded)()
else
    error("Unauthorized execution")
end
"""
        return {
            "success": True,
            "loadstring_id": ls_id,
            "access_key": key,
            "loadstring_code": loadstring_code
        }

db = ZenithDatabase()

# ================= OBFUSCATOR =================
def heavy_obfuscate(code):
    enc = base64.b64encode(code.encode()).decode()[::-1]
    return f"""
local d="{enc}"
local s=d:reverse()
local b=game:GetService("HttpService"):Base64Decode(s)
loadstring(b)()
"""

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
    amount = int(d.get("amount",1))
    ktype = d.get("type","lifetime")
    days = int(d.get("days",0)) if ktype=="day" else None
    keys = db.generate_keys(amount, ktype, days)
    return jsonify({"success": True, "keys": keys})

@app.route("/api/check/<key>")
def check(key):
    return jsonify(db.check_key(key))

@app.route("/api/killswitch/<v>")
def kill(v):
    db.toggle_kill(v=="enable" or v=="on")
    status = "KILL SWITCH ACTIVE" if v=="enable" or v=="on" else "SYSTEM ACTIVE"
    return jsonify({"success": True, "status": status})

@app.route("/api/export/<fmt>")
def export(fmt):
    f = db.export(fmt)
    filename = f"keys.{fmt}"
    with open(filename,"w") as file:
        file.write(f)
    return send_file(filename, as_attachment=True)

@app.route("/api/obfuscate", methods=["POST"])
def obf():
    code = request.json.get("code","")
    if not code or len(code)<10:
        return jsonify({"success": False, "error": "Code too short"})
    return jsonify({"success": True, "obfuscated": heavy_obfuscate(code)})

@app.route("/api/loadstring/create", methods=["POST"])
def ls_create():
    code = request.json.get("code","")
    if not code or len(code)<10:
        return jsonify({"success": False, "error": "Code too short"})
    return jsonify(db.create_loadstring(code))

# ================= RUN SERVER =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=False)
