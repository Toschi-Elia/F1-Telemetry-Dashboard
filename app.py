import streamlit as st
from src.infrastructure.openf1_client import OpenF1Client
from src.core.telemetry import calculate_distance, align_to_distance_grid
from src.presentation.plots import build_telemetry_chart
from src.logger import get_logger
import pandas as pd
import datetime
from src.costants import TEAM_ACRONYMS
from src.infrastructure.circuit_client import CircuitClient
from src.presentation.plots import build_telemetry_chart, build_track_map

logger= get_logger(__name__)

st.set_page_config(page_title="F1 Telemetry Dashboard", layout="wide")

# assicura che si crea una solo volta
@st.cache_resource
def get_client():
    return OpenF1Client()

@st.cache_resource
def get_circuit_client():
    return CircuitClient()

circuit_client = get_circuit_client()


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

st.sidebar.divider() 
show_corners = st.sidebar.checkbox("🏁 Mostra Curve", value=True)
map_position = st.sidebar.radio("Posizione Mappa", ["Alto", "Basso", "Destra", "Sinistra", "Nascosta"], index=1)

# Logica 

@st.cache_data
def process_map(session: int, driver:int):
    df_lap = client.get_fastest_lap(session, driver)
    if df_lap is not None and not df_lap.empty:
        d_start = df_lap["date_start"].values[0]
        lap_dur = df_lap["lap_duration"].values[0]
        d_end = (pd.to_datetime(d_start) + pd.Timedelta(seconds = lap_dur)).isoformat()
        return client.get_location(session, driver, date_start=d_start, date_end=d_end)

    return None



@st.cache_data
def process_driver_telemetry(session: int, driver: int):
    df_lap = client.get_fastest_lap(session, driver)
    if df_lap is None or df_lap.empty:
        return None, None
        
    date_start = df_lap["date_start"].values[0]
    lap_duration = df_lap["lap_duration"].values[0]
    date_start_dt = pd.to_datetime(date_start)
    date_end_dt = date_start_dt + pd.Timedelta(seconds=lap_duration)
    date_end = date_end_dt.isoformat()
    
    df_raw = client.get_car_telemetry(session, driver, date_start=date_start, date_end=date_end)
    if df_raw.empty:
        return None, None
        
    df_dist = calculate_distance(df_raw)
    df_aligned = align_to_distance_grid(df_dist, resolution_m=1.0)
    
    df_info = client.get_driver_info(session, driver)

    driver_info = { 
        "short_label": str(driver),
        "long_label": f"Pilota {driver}",
        "full_name": f"Pilota {driver}",
        "name_acronym": str(driver),
        "team_name": "Sconosciuto",
        "team_acronym": "UNK"
    }
    
    if not df_info.empty:
        nome_completo= df_info["full_name"].values[0]
        nome_abbrev = df_info["name_acronym"].values[0]
        nome_team = df_info["team_name"].values[0]
        team_abbrev = TEAM_ACRONYMS.get(nome_team, nome_team[:3].upper())

        driver_info ={ 
            "full_name": nome_completo,
            "name_acronym": nome_abbrev,
            "team_name": nome_team,
            "team_acronym": team_abbrev,
            "short_label": f"{nome_abbrev} - {team_abbrev}",
            "long_label": f"{nome_completo} - {nome_team}"
        }
         
    return df_aligned, driver_info

if analyze_btn:

    if "Nessun pilota trovato" in driver_option:
        st.error("Dati piloti non disponibili per questa sessione.")
    else:
        driver1 = dict_drivers[selected_driver1_name]
        driver2 = dict_drivers[selected_driver2_name]

        session_row = df_sessions[df_sessions["session_key"] == session_key].iloc[0]
        country_name = session_row["country_name"]
        session_type = session_row["session_name"]


        with st.spinner(f"Estrazione dati per {country_name}..."):
            df1, info1 = process_driver_telemetry(session_key, driver1)
            df2, info2 = process_driver_telemetry(session_key, driver2)

            if df1 is None or df2 is None:
                st.error("Dati telemetrici non trovati per uno dei piloti.")
            else :

                df_location = None
                if map_position != "Nascosta":
                    df_location = process_map(session_key, driver1)

                circuit_info = None
                if show_corners:
                    circuit_info = circuit_client.get_circuit_info(selected_year, country_name, session_type)

                if map_position == "Sinistra":
                    col_map, col_telemetry = st.columns([1,3])

                    with col_map:
                        fig_map = build_track_map(df_location, circuit_info=circuit_info)
                        st.plotly_chart(fig_map, use_container_width=True)

                    with col_telemetry:
                        fig_tel = build_telemetry_chart(df1, df2, info1, info2, circuit_info=circuit_info)
                        st.plotly_chart(fig_tel, use_container_width=True)

                elif map_position == "Destra":
                    col_telemetry, col_map = st.columns([3, 1])
                    with col_telemetry:
                        fig_tel = build_telemetry_chart(df1, df2, info1, info2, circuit_info=circuit_info)
                        st.plotly_chart(fig_tel, use_container_width=True)
                        
                    with col_map:
                        fig_map = build_track_map(df_location, circuit_info=circuit_info)
                        st.plotly_chart(fig_map, use_container_width=True)
                        
                elif map_position == "Basso":
                    fig_tel = build_telemetry_chart(df1, df2, info1, info2, circuit_info=circuit_info)
                    st.plotly_chart(fig_tel, use_container_width=True)

                    _, col_map_center, _ = st.columns([1,2,1])
                    with col_map_center:
                        fig_map = build_track_map(df_location, circuit_info=circuit_info)
                        st.plotly_chart(fig_map, use_container_width=True)

                elif map_position == "Alto":
                    _, col_map_center, _ = st.columns([1, 2, 1])
                    with col_map_center:
                        fig_map = build_track_map(df_location, circuit_info=circuit_info)
                        st.plotly_chart(fig_map, use_container_width=True)

                    fig_tel = build_telemetry_chart(df1, df2, info1, info2, circuit_info=circuit_info)
                    st.plotly_chart(fig_tel, use_container_width=True)

                else:
                    fig_tel = build_telemetry_chart(df1, df2, info1, info2, circuit_info=circuit_info)
                    st.plotly_chart(fig_tel, use_container_width=True)





               