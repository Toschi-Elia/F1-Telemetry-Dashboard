import streamlit as st

from src.infrastructure.openf1_client import OpenF1Client
from src.core.telemetry import calculate_distance, align_to_distance_grid
from src.presentation.plots import build_telemetry_chart
from src.logger import get_logger

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

session_key = st.sidebar.number_input("Session Key (es. 9158 per Monaco Qualy", value=9158, step=1)
driver1 = st.sidebar.number_input("Numero Pilota 1 (es. 1 = Verstappen)", value=1, step=1)
driver2 = st.sidebar.number_input("Numero Pilota 2 (es. 14 = Alonso)", value=14, step=1)

analyze_btn= st.sidebar.button("Analizza Telemetria")


# Logica 

@st.cache_data
def  process_driver_telemetry(session: int, driver: int):
    df_lap= client.get_fastest_lap(session, driver)
    if df_lap is None or df_lap.empty:
        return None, None

    date_start = df_lap["date_start"].values[0]

    df_raw = client.get_car_telemetry(session, driver)
    if df_raw.empty:
         return None, None 

    df_dist = calculate_distance(df_raw)
    df_aligned = align_to_distance_grid(df_dist, resolution_m=1.0)

    df_info= client.get_driver_info(session, driver)
    driver_name = str(driver)

    if not df_info.empty:
        driver_name = df_info["full_name"].values[0]

    return df_aligned, driver_name

if analyze_btn: 
    with st.spinner("Scarico i dati ed eseguo l'allineamento spaziale..."):
        df1, name1= process_driver_telemetry(session_key, driver1)

        df2, name2= process_driver_telemetry(session_key, driver2)

        if df1 is None or df2 is None:
            st.error("Dati non trovati per uno dei piloti nella sessione indicata.")
        else:
            fig = build_telemetry_chart(df1, df2, name1, name2)

            st.plotly_chart(fig, use_container_width=True)