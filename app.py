from flask import Flask, request, jsonify, send_file, render_template
import sqlite3, json, secrets, base64, random, string, hashlib, zlib
from datetime import datetime, timedelta
import os

app = Flask(__name__)
PORT = int(os.environ.get("PORT", 5000))

# ================= ZENITH BALANCED OBFUSCATOR =================
class ZenithBalancedObfuscator:
    def __init__(self):
        self.obf_levels = {
            'light': 1,    # Solo protección básica
            'medium': 2,   # Protección + ofuscación
            'heavy': 3,    # Máxima protección (recomendado)
            'extreme': 4   # Solo para código crítico
        }
    
    def random_name(self):
        """Nombres legibles pero aleatorios"""
        prefixes = ['_Z', '_X', '_Y', '_A', '_B']
        return random.choice(prefixes) + secrets.token_hex(3).upper()
    
    def create_simple_obfuscation(self, code):
        """Ofuscación ligera que mantiene legibilidad"""
        # Header Zenith
        result = "--obfuscated by zenith\n--much love Francy\n\n"
        
        # Solo proteger strings importantes
        strings = re.findall(r'"(?:\\.|[^"\\]){3,}"', code)  # Strings de 3+ chars
        string_map = {}
        
        for s in strings:
            var_name = self.random_name()
            # Encriptación simple pero efectiva
            encoded = base64.b64encode(s.encode()).decode()
            string_map[var_name] = encoded
            code = code.replace(s, var_name)
        
        # Añadir tabla de strings
        if string_map:
            result += "-- Protected strings\n"
            for var_name, encoded in string_map.items():
                result += f'local {var_name} = game:GetService("HttpService"):Base64Decode("{encoded}")\n'
            result += "\n"
        
        # Código principal
        result += code
        return result
    
    def create_balanced_obfuscation(self, code):
        """Balance perfecto entre protección y legibilidad"""
        result = "--obfuscated by zenith\n--much love Francy\n\n"
        
        # Generar clave única
        xor_key = random.randint(100, 200)
        
        # Convertir a bytes y aplicar XOR simple
        code_bytes = code.encode('utf-8')
        encrypted_bytes = [byte ^ xor_key for byte in code_bytes]
        
        # Crear array compacto
        byte_array = []
        chunk = []
        for byte in encrypted_bytes:
            chunk.append(str(byte))
            if len(chunk) >= 15:
                byte_array.append('{' + ','.join(chunk) + '}')
                chunk = []
        
        if chunk:
            byte_array.append('{' + ','.join(chunk) + '}')
        
        # VM simple pero efectiva
        vm_vars = {
            'data': self.random_name(),
            'key': self.random_name(),
            'result': self.random_name()
        }
        
        result += f"""local {vm_vars['data']} = {{
    {',\n    '.join(byte_array)}
}}

local {vm_vars['key']} = {xor_key}
local {vm_vars['result']} = ""

for _, chunk in ipairs({vm_vars['data']}) do
    for _, byte in ipairs(chunk) do
        {vm_vars['result']} = {vm_vars['result']} .. string.char(byte ~ {vm_vars['key']})
    end
end

local func, err = loadstring({vm_vars['result']})
if func then
    func()
else
    error("Load error: " .. tostring(err))
end
"""
        return result
    
    def create_advanced_obfuscation(self, code):
        """Protección avanzada manteniendo compatibilidad"""
        # Header
        result = "--obfuscated by zenith\n--much love Francy\n--advanced protection\n\n"
        
        # Claves de encriptación
        key1 = random.randint(50, 150)
        key2 = random.randint(151, 250)
        
        # Proceso de encriptación en 2 pasos
        step1 = []
        for char in code:
            step1.append(ord(char) ^ key1)
        
        step2 = []
        for byte in step1:
            step2.append(byte ^ key2)
        
        # Fragmentar en partes manejables
        fragments = []
        current = []
        for byte in step2:
            current.append(str(byte))
            if len(current) >= 20:
                fragments.append('{' + ','.join(current) + '}')
                current = []
        
        if current:
            fragments.append('{' + ','.join(current) + '}')
        
        # Generar VM optimizada
        data_var = self.random_name()
        result_var = self.random_name()
        
        result += f"""-- Initialization
local {data_var} = {{{', '.join(fragments)}}}
local {result_var} = ""
local _k1, _k2 = {key1}, {key2}

-- Decryption process
for _, chunk in ipairs({data_var}) do
    for _, byte in ipairs(chunk) do
        local b = tonumber(byte)
        b = b ~ _k2  -- Second layer
        b = b ~ _k1  -- First layer
        {result_var} = {result_var} .. string.char(b)
    end
end

-- Quick integrity check
if #{result_var} > 0 then
    local success, loaded = pcall(loadstring, {result_var})
    if success and loaded then
        loaded()
    else
        warn("Execution failed")
    end
end
"""
        return result
    
    def create_extreme_obfuscation(self, code):
        """Máxima protección manteniendo raw/loadstring funcional"""
        # Header
        result = "--obfuscated by zenith\n--much love Francy\n--extreme protection v2\n\n"
        
        # Comprimir el código
        compressed = zlib.compress(code.encode(), level=9)
        
        # Encriptación multi-nivel pero simple
        key = secrets.token_bytes(16)
        encrypted = bytes(b ^ key[i % 16] for i, b in enumerate(compressed))
        
        # Convertir a array de números legible
        byte_array = []
        line = []
        for i, byte in enumerate(encrypted):
            line.append(str(byte))
            if len(line) >= 12:
                byte_array.append('    {' + ','.join(line) + '},')
                line = []
        
        if line:
            byte_array.append('    {' + ','.join(line) + '}')
        
        # Key en base64 para fácil manejo
        key_b64 = base64.b64encode(key).decode()
        
        # VM optimizada para raw
        result += f"""-- Data block
local _Z_DATA = {{
{chr(10).join(byte_array)}
}}

-- Decryption key
local _Z_KEY = game:GetService("HttpService"):Base64Decode("{key_b64}")

-- Reconstruct bytes
local _Z_BYTES = {{}}
for _, chunk in ipairs(_Z_DATA) do
    for _, byte in ipairs(chunk) do
        table.insert(_Z_BYTES, byte)
    end
end

-- Decrypt
local _Z_DECRYPTED = ""
for i, byte in ipairs(_Z_BYTES) do
    local key_byte = string.byte(_Z_KEY, (i-1) % 16 + 1)
    _Z_DECRYPTED = _Z_DECRYPTED .. string.char(byte ~ key_byte)
end

-- Decompress and execute
local _Z_SUCCESS, _Z_DECOMPRESSED = pcall(function()
    return game:GetService("HttpService"):JSONDecode(_Z_DECRYPTED)
end)

if not _Z_SUCCESS then
    -- Fallback to direct execution
    _Z_DECOMPRESSED = _Z_DECRYPTED
end

-- Final execution (compatible with raw/loadstring)
local _Z_FUNC, _Z_ERR = loadstring(_Z_DECOMPRESSED, "=ZenithProtected")
if _Z_FUNC then
    pcall(_Z_FUNC)
elseif _Z_ERR then
    -- Try without chunkname
    _Z_FUNC = loadstring(_Z_DECOMPRESSED)
    if _Z_FUNC then
        pcall(_Z_FUNC)
    end
end
"""
        return result
    
    def obfuscate(self, code, level='heavy'):
        """Selector de nivel de ofuscación"""
        if level == 'light':
            return self.create_simple_obfuscation(code)
        elif level == 'medium':
            return self.create_balanced_obfuscation(code)
        elif level == 'heavy':
            return self.create_advanced_obfuscation(code)
        elif level == 'extreme':
            return self.create_extreme_obfuscation(code)
        else:
            # Por defecto, balanced
            return self.create_balanced_obfuscation(code)

# Configurar obfuscator
zenith_obfuscator = ZenithBalancedObfuscator()

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
    level = request.json.get("level", "heavy")  # light, medium, heavy, extreme
    
    if not code or len(code)<5:
        return jsonify({"success": False, "error": "Code too short"})
    
    try:
        obfuscated = zenith_obfuscator.obfuscate(code, level)
        return jsonify({
            "success": True, 
            "obfuscated": obfuscated,
            "level": level,
            "size_original": len(code),
            "size_obfuscated": len(obfuscated)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/loadstring/create", methods=["POST"])
def ls_create():
    code = request.json.get("code","")
    if not code or len(code)<10:
        return jsonify({"success": False, "error": "Code too short"})
    return jsonify(db.create_loadstring(code))

# ================= RUN SERVER =================
if __name__ == "__main__":
    print(f"""
    ╔═══════════════════════════════════════════╗
    ║        ZENITH OBFUSCATOR v3.0             ║
    ║        Balanced Protection                ║
    ║        Much love Francy <3                ║
    ║                                           ║
    ║    Server: http://localhost:{PORT}          ║
    ║    Levels: light, medium, heavy, extreme  ║
    ╚═══════════════════════════════════════════╝
    """)
    
    app.run(host="0.0.0.0", port=PORT, debug=False)
