import requests 
import pandas as pd
from typing import Optional

from src.interfaces.data_client import IDataClient
from src.config import settings
from src.logger import get_logger

from pathlib import Path
import re 

logger = get_logger(__name__)

class OpenF1Client(IDataClient):
    """Client per prendere i dati publici """
    def __init__(self):
        self.base_url=settings.OPENF1_BASE_URL
        settings.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"OpenF1Client inizializzato. Base URL: {self.base_url}")


    def _get_cache_path(self, endpoint:str, params: dict)->Path:
        """
        Calcola il percorso univoco del file .parquet per una data richiesta.
        Converte i parametri in una stringa leggibile per il nome del file.
        """
        params_str= "__".join(f"{k}_{v}" for k, v in sorted(params.items()))
        safe_params_str = re.sub(r'[<>:]', '_', params_str)
        filename= f"{endpoint}__{safe_params_str}.parquet"
        return settings.CACHE_DIR/filename
    
    def _fetch_from_api(self, endpoint: str, params: dict)-> pd.DataFrame:
        """
          Implementa il pattern Cache-Aside:
          1. Controlla se esiste già un file .parquet sul disco  -> Cache Hit  (legge dal disco)
          2. Se non esiste                                       -> Cache Miss (chiama l'API e salva)
        """
        cache_path= self._get_cache_path(endpoint,params)

        # cache HIT
        if cache_path.exists():
            logger.info(f"Cache HIT: carico dati locali da '{cache_path.name}'")
            return pd.read_parquet(cache_path)

        # cache MISS
        logger.info(f"Cache MISS: chiamo l'API per '{endpoint}' con {params} ")
        url= f"{self.base_url}/{endpoint}"


        try:
            response= requests.get(url, params=params, timeout=10)
            #solleva eccezione se fallisce 
            response.raise_for_status()
            data= response.json()

            if not data:
                logger.warning(f"Nessun dato trovato per {endpoint} {params}")
                return pd.DataFrame()

            df= pd.DataFrame(data)

            # salvataggio su disco in formato parquet 
            df.to_parquet(cache_path, index=False)
            logger.info(f"Dati salvati in cache: '{cache_path.name}'")

            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"Errore critico di comunicazione con l'API: {e}")
            return pd.DataFrame()


    
    # Implementazione interfaccia 

    def get_car_telemetry(self, session_key: int, driver_number: int, date_start: Optional[str] = None, date_end: Optional[str]=None ) -> pd.DataFrame:
        logger.info(f"Recupero telemetria per pilota {driver_number} (sessione {session_key})")
        params = {"session_key": session_key, "driver_number": driver_number}
        if date_start:
            params["date>"] = date_start
        if date_end:
            params["date<"] = date_end

        return self._fetch_from_api("car_data", params)

    def get_driver_info(self, session_key: int, driver_number: int) -> pd.DataFrame:
        logger.info(f"Recupero info pilota {driver_number} (sessione {session_key})")
        params = {"session_key": session_key, "driver_number": driver_number}
        return self._fetch_from_api("drivers", params)
        

    def get_fastest_lap(self, session_key: int, driver_number: int)-> Optional[pd.DataFrame]:
        logger.info(f"Calcolo giro veloce per pilota {driver_number} (sessione {session_key})")
        params={"session_key": session_key, "driver_number": driver_number}

        #/laps restituisce tutti i giri fatti dal pilota nella sessione 
        df_laps= self._fetch_from_api("laps", params)

        if df_laps.empty:
            return None

        # La colonna "lap_duration" contiene il tempo sul giro in secondi.
        if "lap_duration" in df_laps.columns:
            df_laps= df_laps.dropna(subset=["lap_duration"])
            fastest_lap_row = df_laps.loc[df_laps["lap_duration"].idxmin()]

            #restituiamo dataframe con una riga 
            return pd.DataFrame([fastest_lap_row])
        else:
            logger.error("Dati anomali: colonna 'lap_duration' mancante." )
            return None

    def get_sessions_by_year(self, year: int) -> pd.DataFrame:
        logger.info(f"Recupero sessioni per l'anno {year}")
        return  self._fetch_from_api("sessions", {"year": year})

    def get_drivers_by_session(sefl, session_key):
        logger.info(f"Recupero piloti per la sessione {session_key}")
        df=sefl._fetch_from_api("drivers", {"session_key": session_key})
        if not df.empty:
            df= df.drop_duplicates(subset=["driver_number"])
        return df
    def get_location( self, session_key: int, driver_number: int, date_start: Optional[str] = None, date_end: Optional[str] = None) -> pd.DataFrame:
        logger.info(f"Recupero dati GPS per pilota {driver_number} (sessione {session_key})")
        params = {"session_key": session_key, "driver_number": driver_number}
        if date_start:
            params["date>"] = date_start
        if date_end:
            params["date<"] = date_end

        return self._fetch_from_api("location", params)
    