# F1 Telemetry Dashboard
Un progetto aziendale in Python per l'analisi dei dati telemetrici di F1.

## Architettura del Progetto
Il progetto segue i principi della **Clean Architecture** per garantire la massima modularità. Il cambio della sorgente dati (es. da OpenF1 a FastF1) richiederà esclusivamente la scrittura di una nuova classe in `infrastructure` che implementi l'interfaccia `IDataClient`, senza toccare il livello di business logic (`core`) o la UI (`presentation`).

```plaintext
F1Project/
├── docs/                      # Documentazione tecnica e specifiche
├── src/
│   ├── core/                  # [Domain] Logica pura, modelli matematici (telemetria, interpolazione)
│   ├── interfaces/            # [Ports] Interfacce astratte (es. IDataClient)
│   ├── infrastructure/        # [Adapters] Implementazioni concrete (es. OpenF1Client, salvataggio Parquet)
│   ├── presentation/          # [UI] Generazione grafici e layout (Plotly)
│   ├── config.py              # Gestione configurazione via pydantic e .env
│   └── logger.py              # Logger strutturato aziendale
├── tests/                     # Suite di Unit Test (pytest)
└── app.py                     # Entrypoint Streamlit (dipende da interfaces, inietta infrastructure)
```

## Setup
1. Crea un virtual environment: `python -m venv .venv`
2. Attiva il venv: `.\.venv\Scripts\Activate.ps1` (su Windows)
3. Installa i requisiti: `pip install -r requirements.txt`
4. Avvia l'app: `streamlit run app.py`
