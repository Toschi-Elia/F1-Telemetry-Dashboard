import requests 
import pandas as pd
from typing import Optional

from src.interfaces.data_client import IDataClient
from src.config import settings
from src.logger import get_logger

logger = get_logger(__name__)

class OpenF1Client(IDataClient):
    """Client per prendere i dati publici """
    def __init__(self):
        self.base_url=settings.OPENF1_BASE_URL
        logger.info(f"OpenF1Client inizializzato. Base URL: {self.base_url}")

    def _fetch_from_api(self, endpoint: str, params: dict)-> pd.DataFrame:
        """
        Medoto per fare le chiamate HTTP e convertire JSON in DataFrame  
        """
        url=f"{self.base_url}/{endpoint}"
        logger.debug(f"Chiamata API a: {url} con parametri {params}")

        try:
            response= requests.get(url, params=params, timeout=10)
            #solleva eccezione se fallisce 
            response.raise_for_status()

            data= response.json()

            if not data:
                logger.warning(f"Nessun dato trovato per {endpoint} {params}")
                return pd.DataFrame(data)

            return pd.DataFrame(data)

        except requests.exceptions.RequestException as e:
            logger.error(f"Errore critico di comunicazione con l'API: {e}")
            return pd.DataFrame()


    # Implementazione interfaccia 

    def get_car_telemetry(self, session_key: int, driver_number: int) -> pd.DataFrame:
        logger.info(f"Recupero telemetria per pilota {driver_number} (sessione {session_key})")
        params = {"session_key": session_key, "driver_number": driver_number}
        return self._fetch_from_api("car_data", params)

    def get_driver_info(self, session_key: int, driver_number: int) -> pd.DataFrame:
            logger.info(f"Recupero info pilota {driver_number} (sessione {session_key})")
            params = {"session_key": session_key, "driver_number": driver_number}
            return self._fetch_from_api("drivers", params)
        

    def get_fastest_lap(self, session_key: int, driver_number: int)-> Optional[pd.DataFrame]:
        logger.info(f"Calcolo giro veloce per pilta {driver_number} (sessione {session_key})")
        params={"session_key": session_key, "driver_number": driver_number}

        #/laps restituisce tutti i giri fatti dal pilota nella sessione 
        df_laps= self._fetch_from_api("laps", params)

        if df_laps.empty:
            return None

        # La colonna "lap_duration" contiene il tempo sul giro in secondi.
        if "lap_duration" in df_laps.columns:
            fastest_lap_row = df_laps.loc[df_laps["lap_duration"].idxmin()]

            #restituiamo dataframe con una riga 
            return pd.DataFrame([fastest_lap_row])
        else:
            logger.error("Dati anomali: colonna 'lap_duration' mancante." )
            return None
        


    