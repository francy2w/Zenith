from flask import Flask, request, jsonify, send_file, render_template_string
import sqlite3, json, secrets, base64, hashlib
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
            expires_at TEXT
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

    def check_key(self, key):
        c = self.conn.cursor()
        c.execute("SELECT * FROM keys WHERE key=?", (key,))
        k = c.fetchone()
        if not k:
            return {"valid": False}

        c.execute("SELECT kill_switch FROM config LIMIT 1")
        ks = c.fetchone()
        if ks and ks[0] == 1:
            return {"valid": False}

        if k[5] and datetime.utcnow() > datetime.fromisoformat(k[5]):
            return {"valid": False}

        return {"valid": True, "type": k[2], "expires_at": k[5]}

    def stats(self):
        c = self.conn.cursor()
        return {
            "total": c.execute("SELECT COUNT(*) FROM keys").fetchone()[0],
            "active": c.execute("SELECT COUNT(*) FROM keys WHERE status='active'").fetchone()[0],
            "loadstrings": c.execute("SELECT COUNT(*) FROM loadstrings").fetchone()[0],
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
            return json.dumps([{"key":k[0],"type":k[1],"expires":k[2]} for k in data], indent=2)
        if fmt == "csv":
            return "key,type,expires\n" + "\n".join(f"{k[0]},{k[1]},{k[2]}" for k in data)
        return "\n".join(f"{k[0]} | {k[1]} | {k[2] or 'Lifetime'}" for k in data)

    def create_loadstring(self, code):
        access_key = secrets.token_hex(16)
        encoded = base64.b64encode(code.encode()).decode()
        ls_id = "LS" + secrets.token_hex(10)

        c = self.conn.cursor()
        c.execute(
            "INSERT INTO loadstrings (loadstring_id, encrypted_code, access_key) VALUES (?,?,?)",
            (ls_id, encoded, access_key)
        )
        self.conn.commit()

        lua = f'''
local k="{access_key}"
if _G.ZenithAccessKey~=k then return end
local d="{encoded}"
local s=game:GetService("HttpService"):Base64Decode(d)
loadstring(s)()
'''

        return {"id": ls_id, "access_key": access_key, "loadstring": lua}

db = ZenithDatabase()

# ================= OBFUSCATOR (PESADO) =================
def heavy_obfuscate(code):
    step1 = base64.b64encode(code.encode()).decode()
    step2 = step1[::-1]
    step3 = base64.b64encode(step2.encode()).decode()

    return f'''
local a="{step3}"
local b=game:GetService("HttpService"):Base64Decode(a)
local c=b:reverse()
local d=game:GetService("HttpService"):Base64Decode(c)
loadstring(d)()
'''

# ================= FRONTEND =================
INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Zenith</title>
<style>
body{background:#0b0b0b;color:#0ff;font-family:monospace;text-align:center}
button{padding:10px;margin:5px}
textarea{width:90%;height:120px;background:#000;color:#0f0}
</style>
</head>
<body>
<h1>ZENITH SYSTEM</h1>
<button onclick="gen()">Generate Key</button>
<button onclick="stats()">Stats</button>
<br><br>
<textarea id="code"></textarea><br>
<button onclick="obf()">Obfuscate</button>
<pre id="out"></pre>
<script>
function gen(){
fetch('/api/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({amount:1,type:'lifetime'})})
.then(r=>r.json()).then(d=>out.textContent=JSON.stringify(d,null,2))
}
function stats(){
fetch('/api/stats').then(r=>r.json()).then(d=>out.textContent=JSON.stringify(d,null,2))
}
function obf(){
fetch('/api/obfuscate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({code:code.value})})
.then(r=>r.json()).then(d=>out.textContent=d.obfuscated)
}
</script>
</body>
</html>
"""

# ================= ROUTES =================
@app.route("/")
def index():
    return render_template_string(INDEX_HTML)

@app.route("/api/stats")
def stats():
    return jsonify(db.stats())

@app.route("/api/generate", methods=["POST"])
def generate():
    d = request.json
    return jsonify({"keys": db.generate_keys(int(d["amount"]), d["type"], d.get("days"))})

@app.route("/api/check/<key>")
def check(key):
    return jsonify(db.check_key(key))

@app.route("/api/killswitch/<v>")
def kill(v):
    db.toggle_kill(v == "on")
    return jsonify({"kill_switch": v})

@app.route("/api/export/<fmt>")
def export(fmt):
    f = db.export(fmt)
    name = f"keys.{fmt}"
    open(name,"w").write(f)
    return send_file(name, as_attachment=True)

@app.route("/api/obfuscate", methods=["POST"])
def obf():
    return jsonify({"obfuscated": heavy_obfuscate(request.json["code"])})

@app.route("/api/loadstring/create", methods=["POST"])
def ls_create():
    return jsonify(db.create_loadstring(request.json["code"]))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
