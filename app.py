from flask import Flask, render_template_string, request, jsonify, send_file
import sqlite3, json, secrets, random, base64, hashlib
from datetime import datetime, timedelta
import os, sys

app = Flask(__name__)
PORT = int(os.environ.get("PORT", 5055))

# ==================== DATABASE ====================
class ZenithDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('zenith.db', check_same_thread=False)
        self.init_db()
    
    def init_db(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                key_type TEXT NOT NULL,
                days INTEGER,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                discord_id TEXT DEFAULT '',
                note TEXT DEFAULT ''
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                kill_switch INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS loadstrings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                loadstring_id TEXT UNIQUE,
                encrypted_code TEXT,
                access_key TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
    
    def generate_keys(self, amount, key_type, days=None):
        keys = []
        cursor = self.conn.cursor()
        for _ in range(amount):
            key = f"ZENITH-{secrets.token_hex(8).upper()}"
            expires = None
            if key_type == 'day' and days:
                expires = datetime.now() + timedelta(days=days)
                expires = expires.isoformat()
            cursor.execute('INSERT INTO keys (key, key_type, days, expires_at) VALUES (?, ?, ?, ?)',
                          (key, key_type, days, expires))
            keys.append(key)
        self.conn.commit()
        return keys
    
    def get_stats(self):
        cursor = self.conn.cursor()
        stats = {}
        cursor.execute('SELECT COUNT(*) FROM keys')
        stats['total'] = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM keys WHERE status="active"')
        stats['active'] = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM keys WHERE key_type="lifetime"')
        stats['lifetime'] = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM keys WHERE key_type="day"')
        stats['day'] = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM loadstrings')
        stats['loadstrings'] = cursor.fetchone()[0]
        cursor.execute('SELECT kill_switch FROM config LIMIT 1')
        result = cursor.fetchone()
        stats['kill_switch'] = result[0] if result else 0
        return stats
    
    def toggle_kill_switch(self, state):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE config SET kill_switch = ?', (1 if state else 0,))
        self.conn.commit()
    
    def export_keys(self, format):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM keys')
        keys = cursor.fetchall()
        
        if format == 'txt':
            output = []
            for k in keys:
                expires = k[6] or 'Lifetime'
                output.append(f"{k[1]} | {k[2]} | {expires}")
            return '\n'.join(output)
        elif format == 'json':
            return json.dumps([{'key': k[1], 'type': k[2], 'expires': k[6]} for k in keys], indent=2)
        elif format == 'csv':
            lines = ['key,type,expires']
            for k in keys:
                lines.append(f'{k[1]},{k[2]},{k[6] or "Lifetime"}')
            return '\n'.join(lines)
        return ''
    
    def check_key(self, key):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM keys WHERE key = ?', (key,))
        key_data = cursor.fetchone()
        
        if not key_data:
            return {'valid': False, 'error': 'Key not found'}
        
        cursor.execute('SELECT kill_switch FROM config LIMIT 1')
        if cursor.fetchone()[0] == 1:
            return {'valid': False, 'error': 'System disabled'}
        
        if key_data[6]:
            expires = datetime.fromisoformat(key_data[6])
            if datetime.now() > expires:
                return {'valid': False, 'error': 'Key expired'}
        
        return {'valid': True, 'type': key_data[2], 'discord_id': key_data[7], 'note': key_data[8], 'expires_at': key_data[6]}
    
    def create_loadstring(self, code):
        loadstring_id = f"LS{secrets.token_hex(12).upper()}"
        access_key = secrets.token_hex(16)
        key = secrets.token_hex(8)
        encrypted = self._xor_encrypt(code, key)
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO loadstrings (loadstring_id, encrypted_code, access_key) VALUES (?, ?, ?)',
                       (loadstring_id, encrypted, access_key))
        self.conn.commit()
        loadstring_code = f'''-- Zenith Protected Loadstring
local zenith_data = "{encrypted}"
local zenith_key = "{key}"
local function zenith_decrypt(data,key)
 local r=""
 for i=1,#data do
  r=r..string.char(bit32.bxor(string.byte(data,i),string.byte(key,(i-1)%#key+1)))
 end
 return r
end
if _G.ZenithAccessKey=="{access_key}" then
 local decrypted=zenith_decrypt(zenith_data,zenith_key)
 return loadstring(decrypted)()
else error("Zenith: Unauthorized") end'''
        return {'loadstring_id': loadstring_id,'access_key': access_key,'loadstring_code': loadstring_code,'raw_code': code}
    
    def execute_loadstring(self, loadstring_id, access_key):
        cursor = self.conn.cursor()
        cursor.execute('SELECT encrypted_code FROM loadstrings WHERE loadstring_id=?',(loadstring_id,))
        result = cursor.fetchone()
        if not result: return {'success': False, 'error': 'Loadstring not found'}
        return {'success': True, 'message': 'Loadstring ready for execution','note':'Set _G.ZenithAccessKey="YOUR_KEY"'}

    def _xor_encrypt(self,text,key):
        return ''.join([chr(ord(text[i])^ord(key[i%len(key)])) for i in range(len(text))])

db = ZenithDatabase()

# ==================== OBFUSCATOR ====================
class ZenithObfuscator:
    def obfuscate_lua(self, code):
        import re
        if not code or len(code)<10: return "-- Zenith Obfuscator: Minimum 10 characters required"
        string_pattern = r'(["\'])(?:(?=(\\?))\2.)*?\1'
        strings = re.findall(string_pattern, code)
        for full_string in strings:
            string_content = full_string[0]
            if len(string_content)>2:
                char_codes = [str(ord(c)) for c in string_content]
                encrypted = f'((function() local t={{ {",".join(char_codes)} }} local s="" for _,c in ipairs(t) do s=s..string.char(c) end return s end)())'
                code = code.replace(f'"{string_content}"', encrypted).replace(f"'{string_content}'", encrypted)
        return f'--[[ OBFUSCATED BY ZENITH ]]--\n\n{code}\n\n--[[ ZENITH PROTECTION ENABLED ]]--\nreturn true'

obfuscator = ZenithObfuscator()

# ==================== LOAD HTML ====================
with open("index.html") as f:
    html_content = f.read()

# ==================== ROUTES ====================
@app.route('/')
def index():
    return render_template_string(html_content, port=PORT)

@app.route('/api/stats')
def api_stats():
    return jsonify(db.get_stats())

@app.route('/api/generate', methods=['POST'])
def api_generate():
    data = request.json
    amount = int(data.get('amount',1))
    key_type = data.get('type','lifetime')
    days = int(data.get('days',30)) if key_type=='day' else None
    keys = db.generate_keys(amount,key_type,days)
    return jsonify({'success': True,'keys': keys})

@app.route('/api/killswitch/<action>')
def api_killswitch(action):
    if action=='enable': db.toggle_kill_switch(True); return jsonify({'success':True,'status':'KILL SWITCH ON'})
    elif action=='disable': db.toggle_kill_switch(False); return jsonify({'success':True,'status':'SYSTEM ACTIVE'})
    return jsonify({'error':'Invalid action'}),400

@app.route('/api/export/<format>')
def api_export(format):
    if format not in ['txt','json','csv']: return jsonify({'error':'Invalid format'}),400
    content = db.export_keys(format)
    filename = f'zenith_keys_{datetime.now().strftime("%Y%m%d")}.{format}'
    with open(filename,'w') as f: f.write(content)
    return send_file(filename, as_attachment=True)

@app.route('/api/check/<key>')
def api_check(key):
    return jsonify(db.check_key(key))

@app.route('/api/obfuscate', methods=['POST'])
def api_obfuscate():
    data = request.json
    code = data.get('code','')
    if not code: return jsonify({'error':'No code provided'}),400
    return jsonify({'success':True,'obfuscated':obfuscator.obfuscate_lua(code)})

@app.route('/api/loadstring/create', methods=['POST'])
def api_loadstring_create():
    data = request.json
    code = data.get('code','')
    if not code: return jsonify({'error':'No code provided'}),400
    result = db.create_loadstring(code)
    return jsonify({'success':True,'loadstring_id':result['loadstring_id'],'access_key':result['access_key'],'loadstring_code':result['loadstring_code'],'note':'Save access_key! Required for execution.'})

@app.route('/api/loadstring/execute/<loadstring_id>', methods=['POST'])
def api_loadstring_execute(loadstring_id):
    data = request.json
    access_key = data.get('access_key','')
    if not access_key: return jsonify({'error':'Access key required'}),400
    return jsonify(db.execute_loadstring(loadstring_id, access_key))

if __name__=='__main__':
    print(f"Zenith Key System running on port {PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False)
