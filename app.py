
from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ✅ 統一資料庫路徑
DB = os.path.join(os.path.dirname(__file__), 'location3.db')

# 初始化資料庫
def init_db():
    print("📂 初始化DB:", DB)
    with sqlite3.connect(DB) as conn:
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

# 首頁
@app.route('/')
def index():
    return render_template('index.html')

# 歷史紀錄頁
@app.route('/logs')
def logs():
    print("📂 讀取DB:", DB)
    records = []
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute('SELECT latitude, longitude, timestamp FROM locations ORDER BY id DESC')
        data = c.fetchall()
        for lat, lon, ts in data:
            records.append({
                'latitude': lat,
                'longitude': lon,
                'timestamp': ts,
                'valid': lat is not None and lon is not None
            })
    return render_template('logs.html', records=records)

# 接收 GPS 資料
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

        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute(
                'INSERT INTO locations (latitude, longitude, timestamp) VALUES (?, ?, ?)',
                (latitude, longitude, timestamp)
            )

        print("✅ 已寫入DB")
        return jsonify({'status': 'success'})

    except Exception as e:
        print("❌ 錯誤：", e)
        return jsonify({'status': 'error', 'msg': str(e)})

# 啟動
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
