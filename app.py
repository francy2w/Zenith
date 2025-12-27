from flask import Flask, request, jsonify, send_file, render_template
import sqlite3, json, secrets, base64, random, string, hashlib, zlib, re, time, marshal, ast, types
from datetime import datetime, timedelta
import os

app = Flask(__name__)
PORT = int(os.environ.get("PORT", 5000))

# ================= IRONBREW2 STYLE OBFUSCATOR =================
class Ironbrew2Obfuscator:
    def __init__(self):
        self.variable_counter = 0
        self.string_counter = 0
        self.function_counter = 0
    
    def generate_vm_name(self):
        """Genera nombres de VM como Ironbrew2"""
        prefixes = ["_I", "_X", "_Z", "_A", "_B", "_C"]
        return random.choice(prefixes) + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    def obfuscate_string(self, s):
        """Ofusca strings con múltiples capas"""
        # Capa 1: Base64
        b64 = base64.b64encode(s.encode()).decode()
        
        # Capa 2: XOR con clave aleatoria
        key = random.randint(1, 255)
        xor_result = ''.join(chr(ord(c) ^ key) for c in b64)
        
        # Capa 3: Convertir a decimales
        decimal_array = [str(ord(c)) for c in xor_result]
        
        return f'loadstring((function() local s="" for _,v in ipairs({{{",".join(decimal_array)}}}) do s=s..string.char(v~{key}) end return game:GetService("HttpService"):Base64Decode(s) end)())()'
    
    def generate_constant_obfuscation(self, value):
        """Ofusca constantes como Ironbrew2"""
        if isinstance(value, int):
            methods = [
                lambda x: f'math.floor({x}.5)',
                lambda x: f'tonumber("{x}")',
                lambda x: f'({x}<<0)',
                lambda x: f'bit32.bxor({x},0)',
                lambda x: f'string.len("{x}")',
                lambda x: f'(function() return {x} end)()'
            ]
            return random.choice(methods)(value)
        return value
    
    def create_vm_protection(self):
        """Crea protección de VM estilo Ironbrew2"""
        vm_code = '''
-- Ironbrew2 Virtual Machine Protection
local {vm_name} = (function()
    local {env} = getfenv or function() return _G end
    local {mem} = {{}}
    local {reg} = {{}}
    local {pc} = 1
    local {running} = true
    
    local {opcodes} = {{
        [0] = function() {reg}[1] = {mem}[{pc}+1] {pc} = {pc}+2 end,
        [1] = function() {reg}[2] = {reg}[1] ~ {mem}[{pc}+1] {pc} = {pc}+2 end,
        [2] = function() {mem}[{reg}[1]] = {reg}[2] {pc} = {pc}+1 end,
        [3] = function() {running} = false end
    }}
    
    return function(bytecode)
        for i, v in ipairs(bytecode) do
            {mem}[i] = v
        end
        
        while {running} do
            local op = {mem}[{pc}]
            if {opcodes}[op] then
                {opcodes}[op]()
            else
                {pc} = {pc} + 1
            end
        end
        return {mem}[{reg}[1]]
    end
end)()
'''
        # Reemplazar variables con nombres aleatorios
        replacements = {
            '{vm_name}': self.generate_vm_name(),
            '{env}': self.generate_vm_name(),
            '{mem}': self.generate_vm_name(),
            '{reg}': self.generate_vm_name(),
            '{pc}': self.generate_vm_name(),
            '{running}': self.generate_vm_name(),
            '{opcodes}': self.generate_vm_name()
        }
        
        for old, new in replacements.items():
            vm_code = vm_code.replace(old, new)
        
        return vm_code
    
    def create_anti_tamper(self):
        """Crea protección anti-tamper"""
        anti_tamper = '''
-- Anti-Tamper Protection
(function()
    local {check_env} = getfenv or function() return _G end
    local {env} = {check_env}()
    
    -- Check for common exploit functions
    local {dangerous} = {{
        "hookfunction", "newcclosure", "checkcaller",
        "getscripts", "getloadedmodules", "getgc",
        "getrenv", "getreg", "getinstances"
    }}
    
    for _, {func_name} in ipairs({dangerous}) do
        if env[{func_name}] then
            -- Corrupt execution if tampering detected
            while true do
                math.randomseed(os.time())
                if math.random() > 0.999 then break end
            end
        end
    end
    
    -- Check execution speed (anti-debug)
    local {start} = os.clock()
    for i = 1, 1000000 do end
    local {duration} = os.clock() - {start}
    if {duration} < 0.01 then
        loadstring("while true do end")()
    end
end)()
'''
        # Reemplazar variables
        replacements = {
            '{check_env}': self.generate_vm_name(),
            '{env}': self.generate_vm_name(),
            '{dangerous}': self.generate_vm_name(),
            '{func_name}': self.generate_vm_name(),
            '{start}': self.generate_vm_name(),
            '{duration}': self.generate_vm_name()
        }
        
        for old, new in replacements.items():
            anti_tamper = anti_tamper.replace(old, new)
        
        return anti_tamper
    
    def obfuscate_lua(self, code):
        """Ofusca código Lua estilo Ironbrew2"""
        
        # Header Ironbrew2
        header = "--[[ Ironbrew2 Obfuscation ]]--\n"
        
        # Paso 1: Encriptar strings
        strings = re.findall(r'"(?:\\.|[^"\\])*"', code)
        for s in strings:
            if len(s) > 5:
                obfuscated = self.obfuscate_string(s[1:-1])
                code = code.replace(s, f'({obfuscated})')
        
        # Paso 2: Ofuscar números
        numbers = re.findall(r'\b\d+\b', code)
        for num in numbers:
            if int(num) < 1000:
                obfuscated_num = self.generate_constant_obfuscation(int(num))
                code = code.replace(num, str(obfuscated_num))
        
        # Paso 3: Comprimir y encriptar código
        compressed = zlib.compress(code.encode())
        encrypted = bytearray()
        key = random.randint(1, 255)
        for byte in compressed:
            encrypted.append(byte ^ key)
        
        # Convertir a array Lua
        byte_array = ','.join(str(b) for b in encrypted)
        
        # Paso 4: Construir código final
        obfuscated = header
        
        # Añadir protección anti-tamper
        obfuscated += self.create_anti_tamper() + '\n\n'
        
        # Añadir VM
        obfuscated += self.create_vm_protection() + '\n\n'
        
        # Código para decodificar y ejecutar
        decrypt_func = self.generate_vm_name()
        exec_func = self.generate_vm_name()
        bytecode_var = self.generate_vm_name()
        result_var = self.generate_vm_name()
        
        obfuscated += f'''
local {bytecode_var} = {{{byte_array}}}

local function {decrypt_func}(data, key)
    local result = ""
    for i, v in ipairs(data) do
        result = result .. string.char(v ~ key)
    end
    return result
end

local {result_var} = {decrypt_func}({bytecode_var}, {key})

-- Descomprimir
local success, decompressed = pcall(function()
    return loadstring({result_var})
end)

if not success then
    -- Intentar con zlib decompression
    decompressed = loadstring(zlib.decompress({result_var}))
end

if decompressed then
    setfenv(decompressed, getfenv())
    pcall(decompressed)
end
'''
        
        return obfuscated

# ================= DATABASE =================
class ZenithDatabase:
    def __init__(self):
        self.conn = sqlite3.connect("zenith.db", check_same_thread=False)
        self.init_db()
        self.obfuscator = Ironbrew2Obfuscator()

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
            return {"valid": False, "error": "Key not found"}

        c.execute("SELECT kill_switch FROM config LIMIT 1")
        ks = c.fetchone()
        if ks and ks[0] == 1:
            return {"valid": False, "error": "System disabled"}

        if k[6]:
            if datetime.utcnow() > datetime.fromisoformat(k[6]):
                return {"valid": False, "error": "Key expired"}

        return {"valid": True, "type": k[2], "expires_at": k[6]}

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
    if not code or len(code)<10:
        return jsonify({"success": False, "error": "Code too short"})
    
    obfuscated = db.obfuscator.obfuscate_lua(code)
    return jsonify({"success": True, "obfuscated": obfuscated})

@app.route("/api/loadstring/create", methods=["POST"])
def ls_create():
    code = request.json.get("code","")
    if not code or len(code)<10:
        return jsonify({"success": False, "error": "Code too short"})
    return jsonify(db.create_loadstring(code))

# ================= RUN SERVER =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=False)
