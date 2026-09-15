from pydantic_settings import BaseSettings, SettingsConfigDict 
from pathlib import Path

class Settings(BaseSettings):
    # Gestisce le variabili di configurazione dell'app 

    OPENF1_BASE_URL: str="https://api.openf1.org/v1"

    CACHE_DIR: Path= Path("data/cache")

    DEBUG_MODE: bool =True

    # Pydantic cercherà un file .env nella root del progetto per sovrascrivere 
    model_config= SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

settings= Settings()

