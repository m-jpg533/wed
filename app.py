from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

# 資料庫路徑（避免 Render 出錯）
DB_PATH = os.path.join(os.path.dirname(__file__), 'location.db')

# 初始化資料庫
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latitude REAL,
            longitude REAL,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logs')
def logs():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT latitude, longitude, timestamp FROM locations ORDER BY id DESC')
    data = c.fetchall()
    conn.close()

    records = []
    for lat, lon, ts in data:
        records.append({
            'latitude': lat,
            'longitude': lon,
            'timestamp': ts
        })

    return render_template('logs.html', records=records)

@app.route('/save-location', methods=['POST'])
def save_location():
    try:
        data = request.json
        print("🔥 收到資料：", data)

        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if latitude is None or longitude is None:
            return jsonify({'status': 'error', 'msg': '資料錯誤'})

        timestamp = datetime.now().isoformat()

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            'INSERT INTO locations (latitude, longitude, timestamp) VALUES (?, ?, ?)',
            (latitude, longitude, timestamp)
        )
        conn.commit()
        conn.close()

        return jsonify({'status': 'success'})

    except Exception as e:
        print("❌ 錯誤：", e)
        return jsonify({'status': 'error', 'msg': str(e)})

# 啟動
init_db()

if __name__ == '__main__':
    app.run()

