import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def build_telemetry_chart( df1: pd.DataFrame, df2: pd.DataFrame, driver1_name: str, driver2_name: str)-> go.Figure: 
    """
    Costruisce un grafo interattivo multi-asse per confrontare 2 piloti 
    """

    fig = make_subplots(rows=4, cols=1, shared_xaxes=True,vertical_spacing=0.05, subplot_titles=("Velocità (km/h)", "Acceleratore (%)", "Freno (%)", "Marcia"))

    color1= "#00FFFF"
    color2= "#FF00FF"

    # -- Velocità --
    fig.add_trace(go.Scatter(x=df1['distance_m'], y=df1['speed'], name=f"{driver1_name} Speed", line=dict(color=color1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df2['distance_m'], y=df2['speed'], name=f"{driver2_name} Speed", line=dict(color=color2)), row=1, col=1)

    # -- Acceleratore --
    fig.add_trace(go.Scatter(x=df1['distance_m'], y=df1['throttle'], name = f"{driver1_name} Throttle", line=dict(color=color1)), row=2, col=1)
    fig.add_trace(go.Scatter(x=df2['distance_m'], y=df2['throttle'], name = f"{driver2_name} Throttle", line=dict(color=color2)), row=2, col=1)

    # -- Freno --
    fig.add_trace(go.Scatter(x=df1['distance_m'], y=df1['brake'], name=f"{driver1_name} Brake", line=dict(color=color1)), row=3, col=1)
    fig.add_trace(go.Scatter(x=df2['distance_m'], y=df2['brake'], name=f"{driver2_name} Brake", line=dict(color=color2)), row=3, col=1)

    # -- Marcia -- 
    fig.add_trace(go.Scatter(x=df1['distance_m'], y=df1['n_gear'], name=f"{driver1_name} Gear", line=dict(color=color1)), row=4, col=1)
    fig.add_trace(go.Scatter(x=df2['distance_m'], y=df2['n_gear'], name=f"{driver2_name} Gear", line=dict(color=color2)), row=4, col=1)

    fig.update_layout(height= 900, template= "ploty_dark", title_text =f"Confronto Telemetrico: {driver1_name} vs {driver2_name}", hermode=" x unified")

    fig.update_xaxes(title_text="Distanza (metri)", row=4, col=1)

    return fig 