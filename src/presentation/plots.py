import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def build_telemetry_chart( df1: pd.DataFrame, df2: pd.DataFrame, driver1_name: str, driver2_name: str)-> go.Figure: 
    """
    Costruisce un grafo interattivo multi-asse per confrontare 2 piloti 
    """

    fig = make_subplots(rows=4, cols=1, shared_xaxes=True,vertical_spacing=0.05, subplot_titles=("Velocità (km/h)", "Acceleratore (%)", "Freno (%)", "Marcia"))

    color1= "#0300A3"
    color2= "#920000"

    # -- Velocità --
    fig.add_trace(go.Scatter(x=df1['distance_m'], y=df1['speed'], name=driver1_name, legendgroup=driver1_name, showlegend=True, line=dict(color=color1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df2['distance_m'], y=df2['speed'], name=driver2_name, legendgroup=driver2_name, showlegend=True, line=dict(color=color2)), row=1, col=1)

    # -- Acceleratore --
    fig.add_trace(go.Scatter(x=df1['distance_m'], y=df1['throttle'], legendgroup=driver1_name, showlegend=False, line=dict(color=color1)), row=2, col=1)
    fig.add_trace(go.Scatter(x=df2['distance_m'], y=df2['throttle'], legendgroup=driver2_name, showlegend=False, line=dict(color=color2)), row=2, col=1)

    # -- Freno --
    fig.add_trace(go.Scatter(x=df1['distance_m'], y=df1['brake'], legendgroup=driver1_name, showlegend=False, line=dict(color=color1)), row=3, col=1)
    fig.add_trace(go.Scatter(x=df2['distance_m'], y=df2['brake'], legendgroup=driver2_name, showlegend=False, line=dict(color=color2)), row=3, col=1)

    # -- Marcia -- 
    fig.add_trace(go.Scatter(x=df1['distance_m'], y=df1['n_gear'], legendgroup=driver1_name, showlegend=False, line=dict(color=color1)), row=4, col=1)
    fig.add_trace(go.Scatter(x=df2['distance_m'], y=df2['n_gear'], legendgroup=driver2_name, showlegend=False, line=dict(color=color2)), row=4, col=1)

    fig.update_layout(
        height=900, 
        template="plotly_dark", 
        title_text=f"Confronto Telemetrico: {driver1_name} vs {driver2_name}", 
        hovermode="x unified"
    )

    fig.update_xaxes(title_text="Distanza (metri)", row=4, col=1)

    return fig 