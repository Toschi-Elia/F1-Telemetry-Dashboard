import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def build_telemetry_chart( df1: pd.DataFrame, df2: pd.DataFrame, info1: dict, info2: dict)-> go.Figure: 
    """
    Costruisce un grafo interattivo multi-asse per confrontare 2 piloti 
    """

    fig = make_subplots(rows=4, cols=1, shared_xaxes=True,vertical_spacing=0.05, subplot_titles=("Velocità (km/h)", "Acceleratore (%)", "Freno (%)", "Marcia"))

    color1= "#0300A3"
    color2= "#920000"

    short1 = info1["short_label"]
    short2 = info2["short_label"] 
    nome_short1= info1["name_acronym"]
    nome_short2= info2["name_acronym"]
    nome_long1= info1["full_name"]
    nome_long2= info2["full_name"]
    team_short1= info1["team_acronym"]
    team_short2= info2["team_acronym"]


    # -- Velocità --
    fig.add_trace(go.Scatter(x=df1['distance_m'], y=df1['speed'], name=nome_short1, legendgroup=short1, showlegend=True, line=dict(color=color1), hovertemplate="%{y:.1f} km/h"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df2['distance_m'], y=df2['speed'], name=nome_short2, legendgroup=short2, showlegend=True, line=dict(color=color2), hovertemplate="%{y:.1f} km/h"), row=1, col=1)

    # -- Acceleratore --
    fig.add_trace(go.Scatter(x=df1['distance_m'], y=df1['throttle'], name=nome_short1, legendgroup=short1, showlegend=False, line=dict(color=color1), hovertemplate="%{y:.1f} %"), row=2, col=1)
    fig.add_trace(go.Scatter(x=df2['distance_m'], y=df2['throttle'], name=nome_short2, legendgroup=short2, showlegend=False, line=dict(color=color2), hovertemplate="%{y:.1f} %" ), row=2, col=1)

    # -- Freno --
    fig.add_trace(go.Scatter(x=df1['distance_m'], y=df1['brake'], name=nome_short1, legendgroup=short1, showlegend=False, line=dict(color=color1), hovertemplate="%{y:.1f} %"), row=3, col=1)
    fig.add_trace(go.Scatter(x=df2['distance_m'], y=df2['brake'], name=nome_short2, legendgroup=short2, showlegend=False, line=dict(color=color2), hovertemplate="%{y:.1f} %"), row=3, col=1)

    # -- Marcia -- 
    fig.add_trace(go.Scatter(x=df1['distance_m'], y=df1['n_gear'], name=nome_short1, legendgroup=short1, showlegend=False, line=dict(color=color1),hovertemplate="Marcia: %{y:.0f}"), row=4, col=1)
    fig.add_trace(go.Scatter(x=df2['distance_m'], y=df2['n_gear'], name=nome_short2, legendgroup=short2, showlegend=False, line=dict(color=color2),hovertemplate="Marcia: %{y:.0f}"), row=4, col=1)

    fig.update_layout(
        height=900, 
        template="plotly_dark", 
        title_text=f"Confronto Telemetrico: {nome_long1} ({team_short1})     VS     {nome_long2} ({team_short2})", 
        hovermode="x unified"
    )

    fig.update_xaxes(title_text="Distanza (metri)", row=4, col=1)

    return fig 