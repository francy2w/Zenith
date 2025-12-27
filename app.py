from flask import Flask, render_template_string, request, jsonify, send_file
import sqlite3, json, secrets, os
from datetime import datetime, timedelta
import io

app = Flask(__name__)
PORT = int(os.environ.get("PORT", 5055))

# ================= DATABASE =================
class ZenithDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('zenith.db', check_same_thread=False)
        self.init_db()

    def init_db(self):
        c = self.conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE,
                key_type TEXT,
                days INTEGER,
                status TEXT DEFAULT "active",
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS loadstrings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                loadstring_id TEXT UNIQUE,
                encrypted_code TEXT,
                access_key TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS config (
                kill_switch INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()

    def generate_keys(self, amount, key_type, days=None):
        keys = []
        c = self.conn.cursor()
        for _ in range(amount):
            key = f"ZENITH-{secrets.token_hex(8).upper()}"
            expires = None
            if key_type == "day" and days:
                expires = (datetime.now() + timedelta(days=int(days))).isoformat()
            c.execute('INSERT INTO keys (key,key_type,days,expires_at) VALUES (?,?,?,?)',
                      (key,key_type,days,expires))
            keys.append(key)
        self.conn.commit()
        return keys

    def get_stats(self):
        c = self.conn.cursor()
        stats = {}
        c.execute('SELECT COUNT(*) FROM keys')
        stats['total'] = c.fetchone()[0]
        c.execute('SELECT COUNT(*) FROM keys WHERE status="active"')
        stats['active'] = c.fetchone()[0]
        c.execute('SELECT COUNT(*) FROM loadstrings')
        stats['loadstrings'] = c.fetchone()[0]
        c.execute('SELECT kill_switch FROM config LIMIT 1')
        stats['kill_switch'] = c.fetchone()[0] if c.fetchone() else 0
        return stats

    def toggle_kill_switch(self, state):
        c = self.conn.cursor()
        c.execute('UPDATE config SET kill_switch=?', (1 if state else 0,))
        self.conn.commit()

    def export_keys(self, format):
        c = self.conn.cursor()
        c.execute('SELECT key,key_type,expires_at FROM keys')
        keys = c.fetchall()
        if format == "txt":
            return "\n".join([f"{k[0]} | {k[1]} | {k[2] or 'Lifetime'}" for k in keys])
        elif format == "json":
            return json.dumps([{"key": k[0], "type": k[1], "expires": k[2]} for k in keys], indent=2)
        elif format == "csv":
            lines = ["key,type,expires"]
            for k in keys:
                lines.append(f"{k[0]},{k[1]},{k[2] or 'Lifetime'}")
            return "\n".join(lines)
        return ""

    def check_key(self, key):
        c = self.conn.cursor()
        c.execute('SELECT key_type, expires_at FROM keys WHERE key=?', (key,))
        result = c.fetchone()
        if not result:
            return {"valid": False, "error": "Key not found"}
        if result[1]:
            expires = datetime.fromisoformat(result[1])
            if datetime.now() > expires:
                return {"valid": False, "error": "Key expired"}
        c.execute('SELECT kill_switch FROM config LIMIT 1')
        if c.fetchone()[0]==1:
            return {"valid": False, "error": "System disabled"}
        return {"valid": True, "type": result[0], "expires_at": result[1]}

    def create_loadstring(self, code):
        loadstring_id = f"LS{secrets.token_hex(12).upper()}"
        access_key = secrets.token_hex(16)
        key = secrets.token_hex(8)
        encrypted = ''.join([chr(ord(c)^ord(key[i%len(key)])) for i,c in enumerate(code)])
        c = self.conn.cursor()
        c.execute('INSERT INTO loadstrings (loadstring_id, encrypted_code, access_key) VALUES (?,?,?)',
                  (loadstring_id, encrypted, access_key))
        self.conn.commit()
        loadstring_code = f'''-- Zenith Protected Loadstring
local data="{encrypted}"
local key="{key}"
local function decrypt(data,key)
 local r=""
 for i=1,#data do
  r=r..string.char(bit32.bxor(string.byte(data,i),string.byte(key,(i-1)%#key+1)))
 end
 return r
end
if _G.ZenithAccessKey=="{access_key}" then
 loadstring(decrypt(data,key))()
else error("Unauthorized") end
'''
        return {"loadstring_id": loadstring_id,"access_key": access_key,"loadstring_code": loadstring_code}

db = ZenithDatabase()

# ================= HTML =================
index_html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Zenith Key System</title>
<style>
body{background:#111;color:#fff;font-family:sans-serif}button{padding:10px;margin:5px}
</style>
</head>
<body>
<h1>Zenith Key System</h1>
<p>Total keys: <span id="totalKeys">0</span></p>
<p>Active: <span id="activeKeys">0</span></p>
<p>Loadstrings: <span id="loadstringCount">0</span></p>

<button onclick="generate()">Generate 1 key</button>
<div id="output"></div>

<script>
async function loadStats(){
 let r=await fetch('/api/stats');r=await r.json();
 document.getElementById('totalKeys').textContent=r.total;
 document.getElementById('activeKeys').textContent=r.active;
 document.getElementById('loadstringCount').textContent=r.loadstrings;
}
async function generate(){
 let r=await fetch('/api/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({amount:1,type:'lifetime'})});
 r=await r.json();
 document.getElementById('output').textContent=r.keys.join(', ');
 loadStats();
}
document.addEventListener('DOMContentLoaded',loadStats);
</script>
</body>
</html>"""

# ================= ROUTES =================
@app.route('/')
def index():
    return render_template_string(index_html)

@app.route('/api/stats')
def api_stats():
    return jsonify(db.get_stats())

@app.route('/api/generate', methods=['POST'])
def api_generate():
    data=request.json
    amount=int(data.get('amount',1))
    key_type=data.get('type','lifetime')
    days=int(data.get('days',30)) if key_type=='day' else None
    keys=db.generate_keys(amount,key_type,days)
    return jsonify({"success":True,"keys":keys})

@app.route('/api/check/<key>')
def api_check(key):
    return jsonify(db.check_key(key))

@app.route('/api/loadstring/create', methods=['POST'])
def api_loadstring_create():
    data=request.json
    code=data.get('code','')
    if not code: return jsonify({"error":"No code provided"}),400
    result=db.create_loadstring(code)
    return jsonify(result)

@app.route('/api/export/<format>')
def api_export(format):
    content=db.export_keys(format)
    f=io.StringIO(content)
    return send_file(io.BytesIO(f.getvalue().encode()),as_attachment=True,download_name=f'zenith.{format}')

# ================= RUN =================
if __name__=="__main__":
    print(f"Zenith running on port {PORT}")
    app.run(host='0.0.0.0',port=PORT)
