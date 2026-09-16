from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional

class IDataClient(ABC):
    """
    Interfaccia base per i client di fetching dati.
    Garantisce che qualsiasi sorgente dati (OpenF1, FastF1, CSV locali)
    rispetti lo stesso contratto verso il resto dell'applicazione.
    """
    
    @abstractmethod
    def get_car_telemetry(self, session_key: int, driver_number: int, date_start: Optional[str] = None, date_end: Optional[str]=None) -> pd.DataFrame:
        """
        Recupera la telemetria grezza della vettura.
        """
        pass

    @abstractmethod
    def get_driver_info(self, session_key: int, driver_number: int) -> pd.DataFrame:
        """
        Recupera le informazioni anagrafiche del pilota.
        """
        pass
    
    @abstractmethod
    def get_fastest_lap(self, session_key: int, driver_number: int) -> Optional[pd.DataFrame]:
        """
        Recupera le tempistiche del giro più veloce.
        """
        pass
