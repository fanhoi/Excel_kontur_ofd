import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

def create_expiration_chart(df):
    df_sorted = df.sort_values('Осталось дней', ascending=False)
    
    fig = go.Figure()
    
    colors = {'Пр.': 'red', 'Кр.': 'orange', 'Пред.': 'yellow', 'Норм.': 'green'}
    
    for status in ['Пр.', 'Кр.', 'Пред.', 'Норм.']:
        df_status = df_sorted[df_sorted['Статус'] == status]
        fig.add_trace(go.Bar(
            x=df_status['Название ККТ'],
            y=df_status['Осталось дней'],
            name=status,
            marker_color=colors[status],
            hovertemplate='<b>%{x}</b><br>Осталось дней: %{y}<br>Статус: ' + status
        ))
    
    fig.update_layout(
        title='',
        xaxis_title='Название ККТ',
        yaxis_title='Осталось дней',
        barmode='group',
        height=600,
        legend_title='Статус'
    )
    
    return fig
