from flask import Flask, request, jsonify, send_file, render_template
import sqlite3, json, secrets, base64, random, string, hashlib, zlib, time, re
from datetime import datetime, timedelta
import os

app = Flask(__name__)
PORT = int(os.environ.get("PORT", 5000))

# =========================
# UTILIDADES
# =========================

def sha(data: str):
    return hashlib.sha256(data.encode()).hexdigest()

def b64e(b: bytes):
    return base64.b64encode(b).decode()

def b64d(s: str):
    return base64.b64decode(s.encode())

# =========================
# VM REAL (BYTECODE)
# =========================

OP_LOADK = 1
OP_XOR   = 2
OP_PRINT= 3
OP_HALT = 255

def compile_to_bytecode(lua_source: str):
    """
    Ejemplo mínimo: NO parsea Lua real,
    solo demo para VM (puedes ampliarlo).
    """
    bc = []
    for line in lua_source.splitlines():
        if "print" in line:
            val = line.split("print")[-1].strip("() ")
            bc.append([OP_LOADK, 1, val])
            bc.append([OP_PRINT, 1])
    bc.append([OP_HALT])
    return bc

# =========================
# OBFUSCADOR + VM PAYLOAD
# =========================

class IronbrewUltra:

    def rn(self):
        chars = string.ascii_letters + string.digits
        return "_" + "".join(random.choice(chars) for _ in range(12))

    def obfuscate_vm(self, lua_code: str):
        bytecode = compile_to_bytecode(lua_code)
        raw = json.dumps(bytecode).encode()
        comp = zlib.compress(raw, 9)

        key = secrets.token_bytes(32)
        enc = bytes(b ^ key[i % len(key)] for i, b in enumerate(comp))

        return {
            "data": b64e(enc),
            "key": b64e(key)
        }

    def vm_loader(self, payload):
        v = self.rn()
        r = self.rn()
        pc = self.rn()

        return f'''
local Http=game:GetService("HttpService")
local function VM(bc)
    local r={{}}
    local pc=1
    while true do
        local ins=bc[pc]
        if not ins then break end
        local op=ins[1]
        if op==1 then
            r[ins[2]]=ins[3]
        elseif op==2 then
            r[ins[2]]=bit32.bxor(r[ins[2]],ins[3])
        elseif op==3 then
            print(r[ins[2]])
        elseif op==255 then
            break
        end
        pc+=1
    end
end

local data=Http:Base64Decode("{payload['data']}")
local key=Http:Base64Decode("{payload['key']}")
local dec={{}}
for i=1,#data do
    dec[i]=string.char(string.byte(data,i)~string.byte(key,(i-1)%#key+1))
end
local json=Http:JSONDecode(zlib.decompress(table.concat(dec)))
VM(json)
'''

obfuscator = IronbrewUltra()

# =========================
# DATABASE
# =========================

class ZenithDatabase:
    def __init__(self):
        self.conn = sqlite3.connect("zenith.db", check_same_thread=False)
        self.init()

    def init(self):
        c = self.conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS keys (
            key TEXT PRIMARY KEY,
            expires TEXT
        )""")
        c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            sid TEXT,
            step INTEGER,
            token TEXT
        )""")
        self.conn.commit()

    def new_key(self, days=None):
        k = "ZENITH-" + secrets.token_hex(8)
        exp = None
        if days:
            exp = (datetime.utcnow() + timedelta(days=days)).isoformat()
        self.conn.execute("INSERT INTO keys VALUES (?,?)",(k,exp))
        self.conn.commit()
        return k

    def check_key(self, k):
        c=self.conn.cursor()
        r=c.execute("SELECT expires FROM keys WHERE key=?",(k,)).fetchone()
        if not r: return False
        if r[0] and datetime.utcnow()>datetime.fromisoformat(r[0]): return False
        return True

db = ZenithDatabase()

# =========================
# RUNTIME STREAMING
# =========================

STREAMS = {}

@app.route("/api/stream/start/<key>")
def stream_start(key):
    if not db.check_key(key):
        return jsonify({"error":"invalid key"}),403
    sid = secrets.token_hex(8)
    token = sha(key)
    STREAMS[sid] = {"step":0,"token":token}
    return jsonify({"sid":sid,"token":token})

@app.route("/api/stream/next/<sid>/<token>")
def stream_next(sid, token):
    s = STREAMS.get(sid)
    if not s or token != s["token"]:
        return jsonify({"error":"invalid session"}),403

    steps = STREAMS_PAYLOAD.get(sid)
    if s["step"] >= len(steps):
        return jsonify({"done":True})

    chunk = steps[s["step"]]
    new_token = sha(chunk + token + str(time.time()))

    s["step"] += 1
    s["token"] = new_token

    return jsonify({
        "chunk": b64e(chunk.encode()),
        "token": new_token
    })

# =========================
# API
# =========================

@app.route("/api/generate", methods=["POST"])
def gen():
    days=request.json.get("days")
    return jsonify({"key":db.new_key(days)})

@app.route("/api/obfuscate", methods=["POST"])
def obf():
    code=request.json.get("code","")
    if len(code)<5:
        return jsonify({"error":"code too short"})
    payload=obfuscator.obfuscate_vm(code)
    loader=obfuscator.vm_loader(payload)

    sid=secrets.token_hex(6)
    STREAMS_PAYLOAD[sid]=[loader[i:i+120] for i in range(0,len(loader),120)]

    return jsonify({"success":True,"stream_id":sid})

STREAMS_PAYLOAD = {}

# =========================
# RUN
# =========================

if __name__=="__main__":
    app.run("0.0.0.0",PORT,debug=False)
