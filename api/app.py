from flask import Flask, jsonify, request
from db import get_connection

app = Flask(__name__)

@app.route("/", methods=["GET"])
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/devices", methods=["GET"])
def get_devices():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT device_id
        FROM measurements
        WHERE device_id IS NOT NULL
        ORDER BY device_id
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    devices = [row[0] for row in rows]

    return jsonify({
        "devices": devices
    })

@app.route("/measurements", methods=["GET"])
def get_measurements():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, group_id, device_id, sensor, value, unit, ts_ms, seq, topic
        FROM measurements
        ORDER BY id DESC
        LIMIT 20
    """)

    rows = cur.fetchall()
    cur.close()
    conn.close()

    result = []
    for row in rows:
        result.append({
            "id": row[0],
            "group_id": row[1],
            "device_id": row[2],
            "sensor": row[3],
            "value": row[4],
            "unit": row[5],
            "ts_ms": row[6],
            "seq": row[7],
            "topic": row[8]
        })

    return jsonify(result)

@app.route("/measurements/latest", methods=["GET"])
def get_latest_measurement():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, group_id, device_id, sensor, value, unit, ts_ms, seq, topic
        FROM measurements
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cur.fetchone()
    cur.close()
    conn.close()

    if row is None:
        return jsonify({"message": "Brak danych"}), 404

    return jsonify({
        "id": row[0],
        "group_id": row[1],
        "device_id": row[2],
        "sensor": row[3],
        "value": row[4],
        "unit": row[5],
        "ts_ms": row[6],
        "seq": row[7],
        "topic": row[8]
    })

@app.route("/measurements/history", methods=["GET"])
def get_measurement_history():
    device_id = request.args.get("device_id")
    sensor = request.args.get("sensor")
    limit = request.args.get("limit", default=20, type=int)

    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT id, group_id, device_id, sensor, value, unit, ts_ms, seq, topic
        FROM measurements
        WHERE 1=1
    """
    params = []

    if device_id:
        query += " AND device_id = %s"
        params.append(device_id)

    if sensor:
        query += " AND sensor = %s"
        params.append(sensor)

    query += " ORDER BY id DESC LIMIT %s"
    params.append(limit)

    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    result = []
    for row in rows:
        result.append({
            "id": row[0],
            "group_id": row[1],
            "device_id": row[2],
            "sensor": row[3],
            "value": row[4],
            "unit": row[5],
            "ts_ms": row[6],
            "seq": row[7],
            "topic": row[8]
        })

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)