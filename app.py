from flask import Flask, request, jsonify, send_file, render_template
import sqlite3, json, secrets, base64, random, string, hashlib, zlib, re, time, marshal, ast
from datetime import datetime, timedelta
import os

app = Flask(__name__)
PORT = int(os.environ.get("PORT", 5000))

class IronbrewUltra:
    def __init__(self):
        self.vc = 0
        self.sc = 0
        self.fc = 0
    
    def rn(self):
        chars = string.ascii_letters + string.digits + '_'
        return '_' + ''.join(random.choice(chars) for _ in range(random.randint(8, 15)))
    
    def se(self, s):
        layers = random.randint(3, 7)
        current = s.encode()
        keys = []
        
        for i in range(layers):
            key = secrets.token_bytes(random.randint(8, 32))
            keys.append(key)
            result = bytearray()
            for j, b in enumerate(current):
                result.append(b ^ key[j % len(key)])
            current = bytes(result)
            
            if random.choice([True, False]):
                current = base64.b64encode(current)
            
            if random.choice([True, False]):
                current = current[::-1]
        
        enc_data = base64.b64encode(current).decode()
        keys_b64 = [base64.b64encode(k).decode() for k in keys]
        
        return f'''
local function {self.rn()}(d,k)
    local r=""
    local kb=k:rep(math.ceil(#d/#k))
    for i=1,#d do r=r..string.char(string.byte(d,i)~string.byte(kb,i)) end
    return r
end
local {self.rn()}=game:GetService("HttpService"):Base64Decode("{enc_data}")
local {self.rn()}=[[{','.join(keys_b64[::-1])}]]
local {self.rn()}=string.split({self.rn()},",")
local {self.rn()}={self.rn()}
for i=#{self.rn()},1,-1 do
    {self.rn()}=game:GetService("HttpService"):Base64Decode({self.rn()}[i])
    {self.rn()}={self.rn()}({self.rn()},{self.rn()})
    if i%2==0 then {self.rn()}={self.rn()}:reverse() end
end
return {self.rn()}
'''
    
    def ce(self, num):
        ops = [
            lambda x: f'(({x}<<3)>>3)',
            lambda x: f'bit32.bxor({x},bit32.bxor({x},{x}))',
            lambda x: f'math.floor(math.sin({x})*1000+{x})',
            lambda x: f'tonumber(string.reverse("{x}"))',
            lambda x: f'({random.randint(1,100)}+{x}-{random.randint(1,100)})',
            lambda x: f'({x}*{random.randint(1,5)}//{random.randint(1,5)})',
            lambda x: f'string.byte(string.char({x}))',
            lambda x: f'({x}~{random.randint(1,255)})~{random.randint(1,255)}',
            lambda x: f'((function()local a={x} for i=1,{random.randint(1,10)} do a=a+math.random(-5,5) end return a end)())',
            lambda x: f'loadstring("return {x}")()'
        ]
        
        result = str(num)
        for _ in range(random.randint(2, 5)):
            result = random.choice(ops)(result if result.isdigit() else num)
        
        return result
    
    def ad(self):
        var1 = self.rn()
        var2 = self.rn()
        var3 = self.rn()
        var4 = self.rn()
        var5 = self.rn()
        var6 = self.rn()
        
        return f'''
local function {var1}()
    local {var2}=getfenv or function()return _G end
    local {var3}={var2}()
    local {var4}={{"\\150\\157\\157\\153","\\147\\145\\164\\147\\143","\\144\\145\\142\\165\\147","\\163\\145\\164\\162\\145\\141\\144"}}
    local {var5}=os.clock()
    for i=1,50000 do end
    if os.clock()-{var5}<0.005 then
        while true do math.random() end
    end
    for _,{var6} in ipairs({var4}) do
        local s=""
        for c in {var6}:gmatch("\\\\(%d+)") do
            s=s..string.char(tonumber(c))
        end
        if {var3}[s] then
            for i=1,math.huge do
                if math.random()>0.99999 then return end
            end
        end
    end
end
{var1}()
'''
    
    def vm(self):
        vm_name = self.rn()
        mem_name = self.rn()
        reg_name = self.rn()
        pc_name = self.rn()
        run_name = self.rn()
        op_name = self.rn()
        
        return f'''
local function {vm_name}(b)
    local {mem_name}, {reg_name}, {pc_name}, {run_name} = {{}}, {{1,2,3,4,5,6,7,8}}, 1, true
    for i,v in ipairs(b) do {mem_name}[i]=v end
    
    local {op_name} = {{
        [32] = function() {reg_name}[{mem_name}[{pc_name}+1]]={mem_name}[{pc_name}+2] {pc_name}={pc_name}+3 end,
        [33] = function() {mem_name}[{mem_name}[{pc_name}+1]]={reg_name}[{mem_name}[{pc_name}+2]] {pc_name}={pc_name}+3 end,
        [34] = function() {reg_name}[{mem_name}[{pc_name}+1]]={reg_name}[{mem_name}[{pc_name}+1]]~{mem_name}[{pc_name}+2] {pc_name}={pc_name}+3 end,
        [35] = function() if {reg_name}[1]==0 then {pc_name}={mem_name}[{pc_name}+1] else {pc_name}={pc_name}+2 end end,
        [36] = function() {run_name}=false end,
        [37] = function() table.insert({reg_name},{mem_name}[{pc_name}+1]) {pc_name}={pc_name}+2 end,
        [38] = function() {reg_name}[{mem_name}[{pc_name}+1]]=table.remove({reg_name}) {pc_name}={pc_name}+2 end
    }}
    
    while {run_name} do
        local op={mem_name}[{pc_name}]
        if {op_name}[op] then {op_name}[op]() else {pc_name}={pc_name}+1 end
        if {pc_name}>#{mem_name} then break end
    end
    return {reg_name}[1]
end
return {vm_name}
'''
    
    def of(self, code):
        compressed = zlib.compress(code.encode('utf-8'), level=9)
        
        layers = []
        current = compressed
        transformations = []
        
        for _ in range(random.randint(4, 8)):
            if random.choice([0,1]):
                key = secrets.token_bytes(random.randint(16, 64))
                result = bytearray()
                for i, b in enumerate(current):
                    result.append(b ^ key[i % len(key)])
                current = bytes(result)
                transformations.append(('xor', base64.b64encode(key).decode()))
            else:
                current = base64.b64encode(current)
                transformations.append(('b64', ''))
            
            if random.choice([0,1]):
                current = current[::-1]
                transformations.append(('rev', ''))
        
        final_enc = base64.b64encode(current).decode()
        
        byte_array = []
        chunk_size = random.randint(20, 60)
        for i in range(0, len(final_enc), chunk_size):
            chunk = final_enc[i:i+chunk_size]
            byte_array.append(f'"{chunk}"')
        
        order = list(range(len(byte_array)))
        random.shuffle(order)
        order_enc = base64.b64encode(','.join(map(str, order)).encode()).decode()
        
        vars = {k: self.rn() for k in ['data', 'order', 'assembled', 'step', 'key', 'dec', 'vm_func', 'vm', 'result']}
        
        result = self.ad()
        
        result += f'''
local {vars['data']} = {{{','.join(byte_array)}}}
local {vars['order']} = "{order_enc}"
local {vars['assembled']} = ""
local {vars['order']} = game:GetService("HttpService"):Base64Decode({vars['order']})
local {vars['order']} = string.split({vars['order']},",")
for _,idx in ipairs({vars['order']}) do
    {vars['assembled']} = {vars['assembled']} .. {vars['data']}[tonumber(idx)+1]
end
'''
        
        steps = []
        current_var = vars['assembled']
        
        for i, (ttype, tval) in enumerate(reversed(transformations)):
            step_var = self.rn()
            if ttype == 'rev':
                result += f'local {step_var} = {current_var}:reverse()\n'
                current_var = step_var
            elif ttype == 'b64':
                result += f'local {step_var} = game:GetService("HttpService"):Base64Decode({current_var})\n'
                current_var = step_var
            elif ttype == 'xor':
                key_var = self.rn()
                result += f'local {key_var} = game:GetService("HttpService"):Base64Decode("{tval}")\n'
                result += f'local {step_var} = ""\n'
                result += f'for i=1,#{current_var} do\n'
                result += f'    {step_var}={step_var}..string.char(string.byte({current_var},i)~string.byte({key_var},(i-1)%#{key_var}+1))\n'
                result += f'end\n'
                current_var = step_var
        
        result += f'''
local {vars['dec']} = {current_var}
local {vars['result']}
local success, err = pcall(function()
    {vars['result']} = loadstring({vars['dec']})
end)
if not success then
    success, {vars['result']} = pcall(loadstring, "return "..{vars['dec']})
end
if {vars['result']} then
    setfenv({vars['result']}, getfenv())
    pcall({vars['result']})
end
'''
        
        lines = result.split('\n')
        random.shuffle(lines)
        result = '\n'.join(lines)
        
        result = re.sub(r'\n\s*\n', '\n', result)
        
        return result

obfuscator = IronbrewUltra()

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
        loadstring_code = f"""
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
    obfuscated = obfuscator.of(code)
    return jsonify({"success": True, "obfuscated": obfuscated})

@app.route("/api/loadstring/create", methods=["POST"])
def ls_create():
    code = request.json.get("code","")
    if not code or len(code)<10:
        return jsonify({"success": False, "error": "Code too short"})
    return jsonify(db.create_loadstring(code))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=False)
