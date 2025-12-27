from flask import Flask, request, jsonify, send_file, render_template
import sqlite3, json, secrets, base64, random, string, hashlib, zlib, re
from datetime import datetime, timedelta
import os

app = Flask(__name__)
PORT = int(os.environ.get("PORT", 5000))

# ================= ZENITH BYTECODE OBFUSCATOR =================
class ZenithBytecodeObfuscator:
    def __init__(self):
        pass
    
    def random_name(self):
        """Genera nombres de variables aleatorios"""
        chars = string.ascii_letters + string.digits
        return '_' + ''.join(random.choice(chars) for _ in range(8))
    
    def string_to_octal(self, s):
        """Convierte string a octal escaped"""
        return ''.join(f'\\{ord(c):03o}' for c in s)
    
    def obfuscate_code(self, code):
        """
        Obfuscador con bytecode VM estilo profesional
        """
        
        # Generar nombres únicos
        bytecode_var = self.random_name()
        flat_array_var = self.random_name()
        xor_key_var = self.random_name()
        xor_func_var = self.random_name()
        vm_func_var = self.random_name()
        pc_var = self.random_name()
        buffer_var = self.random_name()
        running_var = self.random_name()
        stack_var = self.random_name()
        env_var = self.random_name()
        anti_func_var = self.random_name()
        op_table_var = self.random_name()
        
        # Generar clave XOR aleatoria
        xor_key = random.randint(100, 250)
        
        # Convertir código a bytes y aplicar XOR
        code_bytes = code.encode('utf-8')
        encrypted_bytes = [byte ^ xor_key for byte in code_bytes]
        
        # Crear bytecode con instrucciones
        opcodes = {
            'PUSH': 48,    # Push valor al stack
            'CHAR': 53,    # Convertir byte a char
            'LOAD': 50,    # Cargar y ejecutar
            'END': 51,     # Terminar ejecución
            'SKIP': 52     # Saltar instrucción
        }
        
        # Construir bytecode array
        bytecode_chunks = []
        current_chunk = []
        
        for byte in encrypted_bytes:
            # Instrucción PUSH seguida del byte
            current_chunk.append(opcodes['PUSH'])
            current_chunk.append(byte)
            
            # Instrucción CHAR para convertir
            current_chunk.append(opcodes['CHAR'])
            
            if len(current_chunk) >= 24:
                bytecode_chunks.append(current_chunk)
                current_chunk = []
        
        # Añadir instrucciones finales
        current_chunk.append(opcodes['LOAD'])
        current_chunk.append(opcodes['END'])
        
        if current_chunk:
            bytecode_chunks.append(current_chunk)
        
        # Construir el código ofuscado SIN comentarios
        obfuscated = f"local {bytecode_var} = {{{{{','.join([','.join(map(str, chunk)) for chunk in bytecode_chunks])}}}}}\n"
        obfuscated += f"local {flat_array_var} = {{}}\n"
        obfuscated += f"for _, c in ipairs({bytecode_var}) do\n"
        obfuscated += f"    for _, b in ipairs(c) do\n"
        obfuscated += f"        table.insert({flat_array_var}, b)\n"
        obfuscated += f"    end\n"
        obfuscated += f"end\n"
        
        obfuscated += f"local {xor_key_var} = {xor_key}\n"
        
        # Función XOR personalizada
        obfuscated += f"local function {xor_func_var}(a, b)\n"
        obfuscated += f"    local r, p = 0, 1\n"
        obfuscated += f"    while a > 0 or b > 0 do\n"
        obfuscated += f"        if (a % 2) ~= (b % 2) then\n"
        obfuscated += f"            r = r + p\n"
        obfuscated += f"        end\n"
        obfuscated += f"        a, b, p = math.floor(a / 2), math.floor(b / 2), p * 2\n"
        obfuscated += f"    end\n"
        obfuscated += f"    return r\n"
        obfuscated += f"end\n"
        
        # Función anti-debug
        debug_strings = [
            self.string_to_octal("hookfunction"),
            self.string_to_octal("getgc"),
            self.string_to_octal("debug"),
            self.string_to_octal("setreadonly")
        ]
        
        obfuscated += f"local function {anti_func_var}()\n"
        obfuscated += f"    local _b = {{{','.join(['"' + s + '"' for s in debug_strings])}}}\n"
        obfuscated += f"    for _, n in ipairs(_b) do\n"
        obfuscated += f"        local _n = \"\"\n"
        obfuscated += f"        for _c in n:gmatch(\"\\\\(%d+)\") do\n"
        obfuscated += f"            _n = _n .. string.char(tonumber(_c))\n"
        obfuscated += f"        end\n"
        obfuscated += f"        local {env_var} = (getfenv and getfenv()) or _G\n"
        obfuscated += f"        if {env_var}[_n] or _G[_n] then\n"
        obfuscated += f"            local _p = (getfenv and getfenv()[\"\\160\\164\\163\\170\\164\"]) or print\n"
        obfuscated += f"            _p(\"\\125\\116\\103\\40\\167\\141\\163\\40\\150\\145\\162\\145\\40\\72\\51\")\n"
        obfuscated += f"            {xor_key_var} = math.random(1, 10000)\n"
        obfuscated += f"            while true do end\n"
        obfuscated += f"        end\n"
        obfuscated += f"    end\n"
        obfuscated += f"end\n"
        
        # Función VM principal
        obfuscated += f"local function {vm_func_var}()\n"
        obfuscated += f"    local {pc_var}, {buffer_var}, {running_var} = 1, {{}}, true\n"
        obfuscated += f"    local {stack_var} = {{}}\n"
        obfuscated += f"    local {env_var} = (getfenv and getfenv()) or _G\n"
        
        # Tabla de opcodes
        obfuscated += f"    local {op_table_var} = {{\n"
        obfuscated += f"        [{opcodes['PUSH']}] = function()\n"
        obfuscated += f"            table.insert({stack_var}, {flat_array_var}[{pc_var} + 1])\n"
        obfuscated += f"            {pc_var} = {pc_var} + 2\n"
        obfuscated += f"        end,\n"
        obfuscated += f"        [{opcodes['CHAR']}] = function()\n"
        obfuscated += f"            local a = table.remove({stack_var})\n"
        obfuscated += f"            table.insert({buffer_var}, string.char({xor_func_var}(a, {xor_key_var})))\n"
        obfuscated += f"            {pc_var} = {pc_var} + 1\n"
        obfuscated += f"        end,\n"
        obfuscated += f"        [{opcodes['LOAD']}] = function()\n"
        obfuscated += f"            {anti_func_var}()\n"
        obfuscated += f"            local _Ll5ax3 = {env_var}[\"\\154\\157\\141\\144\\163\\164\\162\\151\\156\\147\"] or load\n"
        obfuscated += f"            local _SSycka8, _FF9rhas = pcall(_Ll5ax3, table.concat({buffer_var}))\n"
        obfuscated += f"            if _SSycka8 and _FF9rhas then\n"
        obfuscated += f"                local _env = getfenv and getfenv(0) or _G\n"
        obfuscated += f"                setfenv(_FF9rhas, _env)\n"
        obfuscated += f"                pcall(_FF9rhas)\n"
        obfuscated += f"            end\n"
        obfuscated += f"            {pc_var} = {pc_var} + 1\n"
        obfuscated += f"        end,\n"
        obfuscated += f"        [{opcodes['END']}] = function()\n"
        obfuscated += f"            {running_var} = false\n"
        obfuscated += f"        end,\n"
        obfuscated += f"        [{opcodes['SKIP']}] = function()\n"
        obfuscated += f"            {pc_var} = {pc_var} + 2\n"
        obfuscated += f"        end\n"
        obfuscated += f"    }}\n"
        
        obfuscated += f"    {anti_func_var}()\n"
        obfuscated += f"    while {running_var} do\n"
        obfuscated += f"        local c = {flat_array_var}[{pc_var}]\n"
        obfuscated += f"        if not c then break end\n"
        obfuscated += f"        if {op_table_var}[c] then\n"
        obfuscated += f"            {op_table_var}[c]()\n"
        obfuscated += f"        else\n"
        obfuscated += f"            {pc_var} = {pc_var} + 1\n"
        obfuscated += f"        end\n"
        obfuscated += f"    end\n"
        obfuscated += f"end\n"
        
        obfuscated += f"pcall({vm_func_var})"
        
        return obfuscated

obfuscator = ZenithBytecodeObfuscator()

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
    if not code or len(code)<5:
        return jsonify({"success": False, "error": "Code too short"})
    
    # Usar el obfuscador de bytecode
    obfuscated = obfuscator.obfuscate_code(code)
    return jsonify({"success": True, "obfuscated": obfuscated})

@app.route("/api/loadstring/create", methods=["POST"])
def ls_create():
    code = request.json.get("code","")
    if not code or len(code)<10:
        return jsonify({"success": False, "error": "Code too short"})
    return jsonify(db.create_loadstring(code))

# ================= RUN SERVER =================
if __name__ == "__main__":
    # Crear directorio de templates si no existe
    if not os.path.exists("templates"):
        os.makedirs("templates")
    
    # Crear template HTML básico
    with open("templates/index.html", "w") as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Zenith Obfuscator</title>
    <style>
        body { font-family: Arial; margin: 40px; background: #0a0a0a; color: white; }
        .container { max-width: 800px; margin: 0 auto; }
        textarea { width: 100%; height: 200px; background: #111; color: #0f0; border: 1px solid #00f; padding: 10px; }
        button { background: #0066ff; color: white; border: none; padding: 10px 20px; cursor: pointer; margin: 10px 0; }
        .code-output { background: #111; color: #0f0; padding: 15px; margin-top: 10px; border: 1px solid #00f; position: relative; }
        .copy-btn { position: absolute; top: 10px; right: 10px; background: #0066ff; color: white; border: none; padding: 5px 10px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Zenith Obfuscator</h1>
        <textarea id="code" placeholder="Paste your Lua code here...">print("Hello Zenith")</textarea>
        <button onclick="obfuscate()">Obfuscate with Zenith</button>
        <div class="code-output" id="output">
            <!-- Obfuscated code appears here -->
            <button class="copy-btn" onclick="copyCode()">Copy</button>
        </div>
    </div>
    <script>
        async function obfuscate() {
            const code = document.getElementById('code').value;
            const res = await fetch('/api/obfuscate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({code})
            });
            const data = await res.json();
            if(data.success) {
                const output = document.getElementById('output');
                output.innerHTML = `<button class="copy-btn" onclick="copyCode()">Copy</button><pre>${data.obfuscated}</pre>`;
            }
        }
        function copyCode() {
            const code = document.querySelector('#output pre').innerText;
            navigator.clipboard.writeText(code);
            alert('Code copied!');
        }
    </script>
</body>
</html>""")
    
    print(f"""
    ╔═══════════════════════════════════════════╗
    ║        ZENITH Web             ║
    ║        Hello world                          ║
    ║        Much love Francy <3                ║
    ╚═══════════════════════════════════════════╝
    """)
    
    app.run(host="0.0.0.0", port=PORT, debug=False)
