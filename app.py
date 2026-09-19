import streamlit as st

from src.infrastructure.openf1_client import OpenF1Client
from src.core.telemetry import calculate_distance, align_to_distance_grid
from src.presentation.plots import build_telemetry_chart
from src.logger import get_logger
import pandas as pd
import datetime

logger= get_logger(__name__)

st.set_page_config(page_title="F1 Telemetry Dashboard", layout="wide")

# assicura che si crea una solo volta
@st.cache_resource
def get_client():
    return OpenF1Client()

client= get_client()

st.title("🏎️ F1 Telemetry Dashboard")
st.markdown("Confronta la telemetria di due piloti sullo stesso circuito. L'asse X è la **distanza percorsa in metri**, ottenuta integrando la velocità nel tempo e allineata tramite interpolazione.")

st.sidebar.header("Impostazioni")

current_year = datetime.datetime.now().year
avaible_years= list(range(current_year, 2022, -1))

selected_year = st.sidebar.selectbox("Anno del Campionato", avaible_years)

df_sessions = client.get_sessions_by_year(selected_year)
dict_sessions={}

if not df_sessions.empty:
    for _, row in df_sessions.iterrows():
        readable_name= f"{row['country_name']} - {row['session_name']}"
        dict_sessions[readable_name] = row["session_key"]

selected_session_name = st.sidebar.selectbox("Gara e Sessione", options=list(dict_sessions.keys()))
session_key= dict_sessions[selected_session_name]

df_drivers = client.get_drivers_by_session(session_key)
dict_drivers = {}

if not df_drivers.empty:
    df_drivers = df_drivers.sort_values(by="driver_number")
    for _, row in df_drivers.iterrows():
        label = f"{row['full_name']} ({row['driver_number']}) - {row['team_name']}"
        dict_drivers[label] = row["driver_number"]


    

with st.sidebar.form(key="telematry_form"):

    driver_option= list(dict_drivers.keys()) if dict_drivers else ["Nessun pilota trovato"]
    selected_driver1_name= st.selectbox("Pilota 1", options=driver_option, index=0)
    selected_driver2_name= st.selectbox("Pilota 2", options=driver_option, index=1 if len(driver_option) > 1 else 0)
    
    analyze_btn= st.form_submit_button("Analizza Telemetria")


# Logica 

@st.cache_data
def process_driver_telemetry(session: int, driver: int):
    df_lap = client.get_fastest_lap(session, driver)
    if df_lap is None or df_lap.empty:
        return None, None
        
    date_start = df_lap["date_start"].values[0]
    
    lap_duration = df_lap["lap_duration"].values[0]
    date_start_dt = pd.to_datetime(date_start)
    date_end_dt = date_start_dt + pd.Timedelta(seconds=lap_duration)
    # L'API richiede il formato ISO (es. "2023-05-27T14:24:45.123")
    date_end = date_end_dt.isoformat()
    
    #scarichiamo la telemetria SOLO per questo specifico giro!
    df_raw = client.get_car_telemetry(session, driver, date_start=date_start, date_end=date_end)
    if df_raw.empty:
        return None, None

    df_dist = calculate_distance(df_raw)
    df_aligned = align_to_distance_grid(df_dist, resolution_m=1.0)
    
    df_info = client.get_driver_info(session, driver)
    driver_name = str(driver)
    if not df_info.empty:
        nome_pilota = df_info["full_name"].values[0]
        nome_team= df_info["team_name"].values[0]

        driver_name= f"{nome_pilota} - {nome_team}"
    return df_aligned, driver_name

if analyze_btn:

    if "Nessun pilota trovato" in driver_option:
        st.errors("Dati piloti non disponibili per questa sessione.")
    else:
        driver1= dict_drivers[selected_driver1_name]
        driver2 = dict_drivers[selected_driver2_name]

    with st.spinner("Scarico i dati ed eseguo l'allineamento spaziale..."):
        df1, name1 = process_driver_telemetry(session_key, driver1)
        df2, name2 = process_driver_telemetry(session_key, driver2)

        if df1 is None or df2 is None:
            st.error("Dati telemetrici non trovati per uno dei piloti.")
        else :
            fig= build_telemetry_chart(df1, df2, name1, name2)
            st.plotly_chart(fig, use_container_width=True)