import fastf1
import pandas as pd 
import os 
from src.logger import get_logger

logger= get_logger(__name__)

class CircuitClient:
    def __init__(self):
        cache_dir = ".cache_fastf1" 
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        fastf1.Cache.enable_cache(cache_dir)

    def get_circuit_info(self, year: int, country_name: str, session_name: str):
        """
        Scarica i dati e le curve ufficiali utilizzando FastF1. 
        Restituisce un 'CircuitInfo' contenente le coordinate X,Y e le curve 
        """
        try: 
            logger.info(f"FastF1: Scarica geometria circuito {country_name} {year}")

            session= fastf1.get_session(year, country_name, session_name)
            session.load(weather=False, messages=False)
        
            circuit_info = session. get_circuit_info()

            return circuit_info
        except Exception as e:
            logger.info(f"Errore durante l'estrazione della mappa con FastF1: {e}")
            return None