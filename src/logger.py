import logging
import sys
from src.config import settings 

def get_logger(name: str)-> logging.Logger:
    
    # Restituisce un logger configurato 
    logger= logging.getLogger(name)

    # Non lo duplichiamo 
    if not logger.handlers:
        log_level= logging.DEBUG if settings.DEBUG_MODE else logging.INFO
        logger.setLevel(log_level)

        # stampa dei log
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)


        # Definiamo un formato standard: [Data] - [Modulo] - [Livello] - Messaggio
        formatter= logging.Formatter( '%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt ='%Y-%m-%d %H:%M:%S')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    return logger 
    