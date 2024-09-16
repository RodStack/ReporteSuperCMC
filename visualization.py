# visualization.py

import plotly.express as px
import pandas as pd
from config import REGIONS

def create_heatmap(monthly_goals, fiscalized_data):
    # Crear un DataFrame con los datos del mapa de calor
    df_heatmap = pd.DataFrame(monthly_goals, index=REGIONS)
    
    # Calcular el porcentaje de cumplimiento
    for month in df_heatmap.columns:
        for region in df_heatmap.index:
            goal = df_heatmap.loc[region, month]
            achieved = fiscalized_data.get((region, month), 0)
            percentage = min((achieved / goal) * 100 if goal > 0 else 0, 100)
            df_heatmap.loc[region, month] = percentage
    
    # Crear el mapa de calor con Plotly Express
    fig = px.imshow(df_heatmap.values,
                    labels=dict(x="Mes", y="Región", color="Porcentaje"),
                    x=df_heatmap.columns,
                    y=df_heatmap.index,
                    aspect="auto",
                    color_continuous_scale="RdYlGn")  
    
    # Personalizar el diseño
    fig.update_layout(
        title="Mapa Calor Fiscalizados Meta",
        xaxis_title="Mes",
        yaxis_title="Región",
        height=800,
    )
    
    # Añadir los valores en cada celda
    fig.update_traces(text=df_heatmap.values, texttemplate="%{text:.1f}%", textfont={"size":10})
    
    return fig