"""
Python/Streamlit UI dla projektu Rozproszone Systemy Pomiarowe.

Dashboard pełni rolę klienta REST i funkcjonalnie zastępuje panel LabVIEW:
- test połączenia z API,
- pobranie listy device_id,
- pobranie ostatniego pomiaru,
- pobranie historii pomiarów,
- filtrowanie po device_id, sensor i limit,
- prezentacja danych liczbowo, tabelarycznie i graficznie,
- obsługa błędów połączenia i błędnych odpowiedzi API.

Uruchomienie:
    streamlit run ui/app.py
"""

from __future__ import annotations

import time
from typing import Any

import pandas as pd
import streamlit as st

from api_client import ApiClient, ApiClientError
from config import (
    DEFAULT_API_URL,
    DEFAULT_LIMIT,
    DEFAULT_PASSWORD,
    DEFAULT_SENSOR,
    DEFAULT_TIMEOUT,
    DEFAULT_USERNAME,
)


st.set_page_config(
    page_title="RSP Dashboard",
    page_icon="📡",
    layout="wide",
)


def build_client() -> ApiClient:
    """Buduje klienta REST na podstawie aktualnych ustawień z panelu bocznego."""
    return ApiClient(
        base_url=st.session_state.get("api_url", DEFAULT_API_URL),
        username=st.session_state.get("username", ""),
        password=st.session_state.get("password", ""),
        timeout=float(st.session_state.get("timeout", DEFAULT_TIMEOUT)),
    )


def normalize_records(records: list[dict[str, Any]]) -> pd.DataFrame:
    """Zamienia listę rekordów JSON na DataFrame z przewidywalnymi kolumnami."""
    if not records:
        return pd.DataFrame(
            columns=[
                "id",
                "group_id",
                "device_id",
                "sensor",
                "value",
                "unit",
                "ts_ms",
                "seq",
                "topic",
            ]
        )

    df = pd.DataFrame(records)

    expected_columns = [
        "id",
        "group_id",
        "device_id",
        "sensor",
        "value",
        "unit",
        "ts_ms",
        "seq",
        "topic",
    ]

    for column in expected_columns:
        if column not in df.columns:
            df[column] = None

    df = df[expected_columns]
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["ts_ms"] = pd.to_numeric(df["ts_ms"], errors="coerce")
    df["seq"] = pd.to_numeric(df["seq"], errors="coerce")

    return df


def show_latest_record(record: dict[str, Any]) -> None:
    """Wyświetla blok ostatniego pomiaru."""
    st.subheader("Ostatni pomiar")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Value", record.get("value", "—"))

    with col2:
        st.metric("Unit", record.get("unit") or "—")

    with col3:
        st.metric("Sensor", record.get("sensor", "—"))

    with col4:
        st.metric("Seq", record.get("seq", "—"))

    details_col1, details_col2 = st.columns(2)

    with details_col1:
        st.text_input("Device ID", value=str(record.get("device_id", "")), disabled=True)

    with details_col2:
        st.text_input("Timestamp ts_ms", value=str(record.get("ts_ms", "")), disabled=True)

    with st.expander("Pokaż pełny JSON ostatniego pomiaru"):
        st.json(record)


def show_history(records: list[dict[str, Any]]) -> None:
    """Wyświetla tabelę i wykres historii."""
    st.subheader("Historia pomiarów")

    df = normalize_records(records)

    if df.empty:
        st.warning("Brak danych dla wybranych filtrów.")
        return

    # API zwraca dane od najnowszych. Do wykresu wygodniej pokazać od najstarszych.
    df_for_chart = df.sort_values(by=["ts_ms", "id"], ascending=True).reset_index(drop=True)
    df_for_chart["sample"] = range(1, len(df_for_chart) + 1)

    chart_df = df_for_chart[["sample", "value"]].dropna()

    if chart_df.empty:
        st.warning("Dane nie zawierają poprawnych wartości liczbowych do wykresu.")
    else:
        st.line_chart(chart_df, x="sample", y="value", height=360)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )


def load_devices(client: ApiClient) -> list[str]:
    """Pobiera listę urządzeń i zapisuje ją w session_state."""
    devices = client.get_devices()
    st.session_state["devices"] = devices
    return devices


def init_session_state() -> None:
    defaults = {
        "api_url": DEFAULT_API_URL,
        "username": DEFAULT_USERNAME,
        "password": DEFAULT_PASSWORD,
        "timeout": DEFAULT_TIMEOUT,
        "devices": [],
        "selected_device": "",
        "sensor": DEFAULT_SENSOR,
        "limit": DEFAULT_LIMIT,
        "latest_record": None,
        "history_records": [],
        "last_status_message": "",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()

st.title("📡 Rozproszone Systemy Pomiarowe — Python UI")
st.caption(
    "Dashboard działa jako klient REST dla Flask API. "
    "Jest alternatywną implementacją warstwy prezentacji przewidzianej w instrukcji LabVIEW."
)

with st.sidebar:
    st.header("Konfiguracja API")

    st.text_input(
        "API URL",
        key="api_url",
        help="Domyślnie Flask API działa pod adresem http://localhost:5001",
    )

    st.number_input(
        "Timeout HTTP [s]",
        min_value=1.0,
        max_value=60.0,
        step=1.0,
        key="timeout",
    )

    st.divider()

    st.subheader("Basic Auth")
    st.caption("Aktualnie opcjonalne. Po laboratorium 10 wpisz dane logowania API.")

    st.text_input("Username", key="username")
    st.text_input("Password", key="password", type="password")

    st.divider()

    client = build_client()

    if st.button("Test API /health", use_container_width=True):
        try:
            health = client.get_health()
            st.session_state["last_status_message"] = f"API OK: {health}"
            st.success("Połączenie z API działa.")
        except ApiClientError as exc:
            st.session_state["last_status_message"] = str(exc)
            st.error(str(exc))

    if st.button("Odśwież listę urządzeń /devices", use_container_width=True):
        try:
            devices = load_devices(client)
            if devices:
                st.session_state["selected_device"] = devices[0]
                st.success(f"Pobrano {len(devices)} urządzeń.")
            else:
                st.warning("Endpoint /devices zwrócił pustą listę.")
        except ApiClientError as exc:
            st.session_state["last_status_message"] = str(exc)
            st.error(str(exc))

    st.divider()

    auto_refresh = st.checkbox("Auto refresh historii", value=False)
    refresh_interval = st.number_input(
        "Interwał [s]",
        min_value=2,
        max_value=60,
        value=5,
        step=1,
    )


client = build_client()

# Próba automatycznego pobrania urządzeń przy starcie, ale bez blokowania całego UI błędem.
if not st.session_state["devices"]:
    try:
        load_devices(client)
    except ApiClientError:
        pass

devices = st.session_state.get("devices", [])

config_col1, config_col2, config_col3 = st.columns([2, 2, 1])

with config_col1:
    if devices:
        current_device = st.session_state.get("selected_device") or devices[0]
        if current_device not in devices:
            current_device = devices[0]

        selected_device = st.selectbox(
            "Device ID",
            options=devices,
            index=devices.index(current_device),
        )
        st.session_state["selected_device"] = selected_device
    else:
        selected_device = st.text_input(
            "Device ID",
            value=st.session_state.get("selected_device", ""),
            placeholder="np. esp32-E8247EB865E4",
        )
        st.session_state["selected_device"] = selected_device

with config_col2:
    sensor = st.text_input(
        "Sensor",
        value=st.session_state.get("sensor", DEFAULT_SENSOR),
        placeholder="np. temperature",
    )
    st.session_state["sensor"] = sensor

with config_col3:
    limit = st.number_input(
        "Limit",
        min_value=1,
        max_value=500,
        value=int(st.session_state.get("limit", DEFAULT_LIMIT)),
        step=1,
    )
    st.session_state["limit"] = limit

button_col1, button_col2, button_col3 = st.columns(3)

with button_col1:
    get_latest_clicked = st.button("Pobierz latest globalnie", use_container_width=True)

with button_col2:
    get_latest_for_device_clicked = st.button(
        "Pobierz latest dla urządzenia",
        use_container_width=True,
        help="Wykorzystuje /measurements/history z limit=1, żeby uwzględnić wybrany device_id i sensor.",
    )

with button_col3:
    get_history_clicked = st.button("Pobierz historię", use_container_width=True)

if get_latest_clicked:
    try:
        st.session_state["latest_record"] = client.get_latest()
        st.session_state["last_status_message"] = "Pobrano ostatni pomiar globalny."
        st.success("Pobrano ostatni pomiar globalny.")
    except ApiClientError as exc:
        st.session_state["last_status_message"] = str(exc)
        st.error(str(exc))

if get_latest_for_device_clicked:
    try:
        records = client.get_history(
            device_id=st.session_state.get("selected_device") or None,
            sensor=st.session_state.get("sensor") or None,
            limit=1,
        )
        if records:
            st.session_state["latest_record"] = records[0]
            st.session_state["last_status_message"] = "Pobrano ostatni pomiar dla wybranego filtra."
            st.success("Pobrano ostatni pomiar dla wybranego filtra.")
        else:
            st.warning("Brak danych dla wybranego urządzenia/sensora.")
    except ApiClientError as exc:
        st.session_state["last_status_message"] = str(exc)
        st.error(str(exc))

if get_history_clicked or auto_refresh:
    try:
        records = client.get_history(
            device_id=st.session_state.get("selected_device") or None,
            sensor=st.session_state.get("sensor") or None,
            limit=int(st.session_state.get("limit", DEFAULT_LIMIT)),
        )
        st.session_state["history_records"] = records
        st.session_state["last_status_message"] = f"Pobrano historię: {len(records)} rekordów."
        if get_history_clicked:
            st.success(f"Pobrano historię: {len(records)} rekordów.")
    except ApiClientError as exc:
        st.session_state["last_status_message"] = str(exc)
        st.error(str(exc))

status_message = st.session_state.get("last_status_message")
if status_message:
    st.info(status_message)

latest_record = st.session_state.get("latest_record")
history_records = st.session_state.get("history_records", [])

latest_tab, history_tab, diagnostics_tab = st.tabs(
    ["Latest measurement", "Historia i wykres", "Diagnostyka"]
)

with latest_tab:
    if latest_record:
        show_latest_record(latest_record)
    else:
        st.warning("Nie pobrano jeszcze ostatniego pomiaru.")

with history_tab:
    show_history(history_records)

with diagnostics_tab:
    st.subheader("Endpointy używane przez UI")

    base_url = st.session_state.get("api_url", DEFAULT_API_URL).rstrip("/")
    selected_device = st.session_state.get("selected_device", "")
    sensor = st.session_state.get("sensor", DEFAULT_SENSOR)
    limit = st.session_state.get("limit", DEFAULT_LIMIT)

    st.code(
        "\n".join(
            [
                f"GET {base_url}/health",
                f"GET {base_url}/devices",
                f"GET {base_url}/measurements/latest",
                f"GET {base_url}/measurements/history?device_id={selected_device}&sensor={sensor}&limit={limit}",
            ]
        ),
        language="text",
    )

    st.subheader("Stan konfiguracji")
    st.json(
        {
            "api_url": base_url,
            "selected_device": selected_device,
            "sensor": sensor,
            "limit": limit,
            "devices_count": len(devices),
            "auth_enabled": bool(st.session_state.get("username") and st.session_state.get("password")),
        }
    )

    if st.button("Pobierz surowe /measurements", use_container_width=True):
        try:
            measurements = client.get_measurements()
            st.write(f"Liczba rekordów: {len(measurements)}")
            st.dataframe(normalize_records(measurements), use_container_width=True, hide_index=True)
        except ApiClientError as exc:
            st.error(str(exc))

if auto_refresh:
    time.sleep(int(refresh_interval))
    st.rerun()
