import pandas as pd
import numpy as np 
from scipy.interpolate import interp1d
from src.logger import get_logger


logger= get_logger(__name__)

def calculate_distance(df: pd.DataFrame)->pd.DataFrame:
    """
    Calcola la distanza cumulativa percorsa in metri integrando la velocità nel tempo.
    Formula applicata: d_i = d_{i-1} + (v_i / 3.6) * delta_t_i    
    Args:
        df: DataFrame grezzo dell'API con colonne 'date' e 'speed'
    Returns:
        Lo stesso DataFrame con la nuova colonna 'distance_m'
    """
    df=df.copy() 

    df["date"] = pd.to_datetime(df["date"], format='ISO8601')

    df= df.sort_values("date").reset_index(drop=True)

    df["delta_t"] = df["date"].diff().dt.total_seconds()

    df["delta_t"]=df["delta_t"].fillna(0)

    df["distance_m"]=(df["speed"]/3.6 * df["delta_t"]).cumsum()

    df["time_elapsed"] = (df["date"] - df["date"].iloc[0]).dt.total_seconds()

    logger.info(f"Distanza calcolata. Distanza totale giro: {df['distance_m'].max():.0f} m")

    return df 

def align_to_distance_grid(df: pd.DataFrame, resolution_m: float=1.0)->pd.DataFrame:
    """
    Prende i segnali telemetrici su una griglia con distanza uniforme 
    Args:
        df: DataFrame con la colonna 'distance_m' già calcolata
        resolution_m: spazio in metri tra ogni punto della griglia (default: 1 metro)
    Returns:
        Un nuovo DataFrame con punti equidistanti sulla pista
    """

    # definizione colonne 
    SIGNAL_COLUMNS = ["speed", "throttle", "brake", "n_gear", "rpm", "time_elapsed"]

    # creazione griglia 
    max_distance= df["distance_m"].max()
    grid = np.arange(0, max_distance, resolution_m)

    logger.info(f"Interpolazione su grigli di {len(grid)} punti (ogni {resolution_m}m)")

    result = pd.DataFrame({"distance_m": grid})

   
    for col in SIGNAL_COLUMNS:
        if col not in df.columns:
            logger.warning(f"Colonna '{col}' non trovata, la salto.")
            continue

        interp_kind = "nearest" if col== "n_gear" else "linear"
        interpolator = interp1d(df["distance_m"], df[col], kind=interp_kind, bounds_error=False, fill_value="extrapolate")

        result[col] = interpolator(grid)    
    return result 

