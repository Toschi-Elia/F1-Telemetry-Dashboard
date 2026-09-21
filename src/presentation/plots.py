import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def build_telemetry_chart( df1: pd.DataFrame, df2: pd.DataFrame, info1: dict, info2: dict, circuit_info=None)-> go.Figure: 
    """
    Costruisce un grafo interattivo multi-asse per confrontare 2 piloti 
    """

    fig = make_subplots(rows=5, cols=1, shared_xaxes=True, vertical_spacing=0.05, subplot_titles=("Delta Time (s)", "Velocità (km/h)", "Acceleratore (%)", "Freno (%)", "Marcia"))

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

    #-- Delta time --   
    delta_time = df1['time_elapsed'] - df2['time_elapsed']
    fig.add_trace(go.Scatter(x=df1['distance_m'], y=delta_time, name=f"Delta {nome_short1}", showlegend=False, line=dict(color="white", width=2), hovertemplate="Delta: %{y:.3f} s"), row=1, col=1)

    # -- Velocità --
    fig.add_trace(go.Scatter(x=df1['distance_m'], y=df1['speed'], name=nome_short1, legendgroup=short1, showlegend=True, line=dict(color=color1), hovertemplate="%{y:.1f} km/h"), row=2, col=1)
    fig.add_trace(go.Scatter(x=df2['distance_m'], y=df2['speed'], name=nome_short2, legendgroup=short2, showlegend=True, line=dict(color=color2), hovertemplate="%{y:.1f} km/h"), row=2, col=1)

    # -- Acceleratore --
    fig.add_trace(go.Scatter(x=df1['distance_m'], y=df1['throttle'], name=nome_short1, legendgroup=short1, showlegend=False, line=dict(color=color1), hovertemplate="%{y:.1f} %"), row=3, col=1)
    fig.add_trace(go.Scatter(x=df2['distance_m'], y=df2['throttle'], name=nome_short2, legendgroup=short2, showlegend=False, line=dict(color=color2), hovertemplate="%{y:.1f} %" ), row=3, col=1)

    # -- Freno --
    fig.add_trace(go.Scatter(x=df1['distance_m'], y=df1['brake'], name=nome_short1, legendgroup=short1, showlegend=False, line=dict(color=color1), hovertemplate="%{y:.1f} %"), row=4, col=1)
    fig.add_trace(go.Scatter(x=df2['distance_m'], y=df2['brake'], name=nome_short2, legendgroup=short2, showlegend=False, line=dict(color=color2), hovertemplate="%{y:.1f} %"), row=4, col=1)

    # -- Marcia -- 
    fig.add_trace(go.Scatter(x=df1['distance_m'], y=df1['n_gear'], name=nome_short1, legendgroup=short1, showlegend=False, line=dict(color=color1),hovertemplate="Marcia: %{y:.0f}"), row=5, col=1)
    fig.add_trace(go.Scatter(x=df2['distance_m'], y=df2['n_gear'], name=nome_short2, legendgroup=short2, showlegend=False, line=dict(color=color2),hovertemplate="Marcia: %{y:.0f}"), row=5, col=1)

    if circuit_info is not None:
        corner_distances = []
        corner_numbers = []

        y_corner = delta_time.max() + 3

        for _, corner in circuit_info.corners.iterrows():
            dist = corner['Distance']
            num = corner['Number']

            fig.add_vline(x=dist, line_width=1, line_dash="dot", line_color="rgba(255, 255, 255, 0.2)")

            corner_distances.append(dist)
            corner_numbers.append(str(num))

        fig.add_trace(go.Scatter(
            x=corner_distances, 
            y=[y_corner] * len(corner_distances),
            mode="markers+text",
            marker=dict(size=18, color="#959735", line=dict(color="black", width=1.5)), 
            text=corner_numbers,
            textfont=dict(color="black", size=9, family="Arial Black"),
            showlegend=False,
            hoverinfo="skip" 
        ), row=1, col=1)


    fig.update_layout(
        height=1000, 
        template="plotly_dark", 
        title_text=f"Confronto Telemetrico: {nome_long1} ({team_short1})  vs  {nome_long2} ({team_short2})", 
        hovermode="x unified"
    )

    fig.update_xaxes(title_text="Distanza (metri)", row=5, col=1)

    return fig 

def build_track_map(df_location: pd.DataFrame, circuit_info=None)-> go.Figure:
    fig= go.Figure()

    if df_location is not None and not df_location.empty:
        fig.add_trace(go.Scatter(
                    x=df_location['x'], 
                    y=df_location['y'], 
                    mode='lines',
                    line=dict(color='white', width=3),
                    name="Traiettoria",
                    showlegend=False
                ))

    if circuit_info is not None:
        corner_x, corner_y, corner_numbers = [], [], []

        for _, corner in circuit_info.corners.iterrows():
            corner_x.append(corner['X'])
            corner_y.append(corner['Y'])
            corner_numbers.append(str(corner['Number']))

        fig.add_trace(go.Scatter(
                    x=corner_x, 
                    y=corner_y,
                    mode="markers+text",
                    marker=dict(size=14, color="#FFD700", line=dict(color="black", width=1.5)),
                    text=corner_numbers,
                    textfont=dict(color="black", size=9, family="Arial Black"),
                    showlegend=False,
                    hoverinfo="skip"
                ))
    fig.update_layout(
        template="plotly_dark",
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis=dict(showgrid=False, zeroline=False, visible=False, scaleanchor="y", scaleratio=1),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        title_text="Tracciato",
        height=500
    )

    return fig