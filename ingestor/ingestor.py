import json
import paho.mqtt.client as mqtt
from db import get_connection

MQTT_HOST = "broker"
MQTT_PORT = 1883
MQTT_TOPIC = "lab/+/+/+"


def save_measurement(topic, data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO measurements
        (group_id, device_id, sensor, value, unit, ts_ms, seq, topic)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        data.get("group_id"),
        data["device_id"],
        data["sensor"],
        data["value"],
        data.get("unit"),
        data["ts_ms"],
        data.get("seq"),
        topic
    ))
    conn.commit()
    cur.close()
    conn.close()


def is_status_topic(topic):
    return topic.endswith("/status")


def is_valid_measurement(data):
    required = ["device_id", "sensor", "value", "ts_ms"]
    return all(field in data for field in required)


def on_connect(client, userdata, flags, rc):
    print("Connected with result code", rc)
    client.subscribe(MQTT_TOPIC)
    print("Subscribed to topic:", MQTT_TOPIC)


def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)

        if is_status_topic(topic):
            print("Status message ignored:", topic, data)
            return

        if not is_valid_measurement(data):
            print("Invalid measurement payload:", data)
            return

        save_measurement(topic, data)
        print("Saved message from topic:", topic)

    except Exception as e:
        print("Error:", e)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_HOST, MQTT_PORT, 60)
client.loop_forever()