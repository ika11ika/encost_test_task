import dash_mantine_components as dmc
import datetime as dt
import sqlite3
import plotly.express as px
from dataclasses import dataclass

from dash import Input, Output, State
from dash.dcc import Graph
from dash.exceptions import PreventUpdate
from dash.html import Div, H1
from dash_extensions.enrich import (DashProxy, MultiplexerTransform,
                                    ServersideOutputTransform)
from pandas import read_sql

CARD_STYLE = dict(
    withBorder=True, shadow='sm', radius='md', style={'height': '400px'}
)


class EncostDash(DashProxy):
    def __init__(self, **kwargs):
        self.app_container = None
        super().__init__(transforms=[ServersideOutputTransform(),
                                     MultiplexerTransform()], **kwargs)


app = EncostDash(name=__name__)
conn = sqlite3.connect('testDB.db', check_same_thread=False)


@dataclass
class MainDataFrame:
    __df_main = read_sql('select * from sources', conn)
    __df_reasons_info = read_sql(
        'select reason, color from sources group by reason', conn
    )
    __df_pie = read_sql(
        'select reason, sum(duration_min) from sources group by reason', conn
    )
    conn.close()

    state_begin: str = (
        __df_main.sort_values(by="state_begin").state_begin.iloc[0]
    )
    state_end: str = __df_main.sort_values(by="state_end").state_end.iloc[-1]
    shift_day: str = __df_main['shift_day'].iloc[0]
    endpoint_name: str = __df_main['endpoint_name'].iloc[0]
    client_name: str = __df_main['client_name'].iloc[0]

    def get_distinct_reasons(self):
        return self.__df_reasons_info['reason'].tolist()

    def get_states_colors(self):
        return self.__df_reasons_info['color'].tolist()

    def get_pie_df(self):
        return self.__df_pie

    def get_bar_df(self):
        return self.__df_main

    def get_color_map(self):
        color_map = dict(zip(
            self.get_distinct_reasons(),
            self.get_states_colors(),
        ))
        return color_map


def show_general_info():
    df = MainDataFrame()
    state_begin = dt.datetime.fromisoformat(df.state_begin)
    state_end = dt.datetime.fromisoformat(df.state_end)

    return dmc.Col([
        dmc.Card([
            Div(H1('Клиент: ' + df.client_name)),
            Div(
                'Сменный день: ' + df.shift_day,
                style={"font-weight": "bold"}
            ),
            Div(
                'Точка учета: ' + df.endpoint_name,
                style={"font-weight": "bold"}
            ),
            Div(
                f'Начало периода: {state_begin:%H:%M:%S (%d %b %Y)}',
                style={"font-weight": "bold"}
            ),
            Div(
                f'Конец периода: {state_end:%H:%M:%S (%d %b %Y)}',
                style={"font-weight": "bold"}
            ),
            dmc.MultiSelect(
                placeholder='Выберите состояние',
                id='selected_filter',
                clearable=True,
                style={"marginBottom": 10},
                data=df.get_distinct_reasons()
            ),
            dmc.Button('Фильтровать', id='filter_button'),
            ], **CARD_STYLE)
        ], span=6
    )


def show_pie_chart():
    df_pie = MainDataFrame().get_pie_df()
    color_map = MainDataFrame().get_color_map()

    return dmc.Col([
            dmc.Card([
                    Div(
                        Graph(
                            figure=px.pie(
                                df_pie,
                                values='sum(duration_min)',
                                names='reason',
                                hole=0.2,
                                color='reason',
                                color_discrete_map=color_map,
                            ).update_layout(margin=dict(t=0, b=180))
                        ),
                    )
                ], **CARD_STYLE
            )
        ], span=6
    )


def create_gantt_chart():
    df_bar = MainDataFrame().get_bar_df()
    color_map = MainDataFrame().get_color_map()
    custom_fields = [
        'state', 'reason', 'state_begin', 'duration_min',
        'shift_day', 'shift_name', 'operator',
    ]

    figure = px.timeline(
        df_bar,
        x_start='state_begin',
        x_end='state_end',
        y='endpoint_name',
        color='reason',
        color_discrete_map=color_map,
        custom_data=[*custom_fields],
        title='График состояний',
        height=300
    ).update_traces(
        hovertemplate=(
            'Состояние - <b>%{customdata[0]}</b><br>' +
            'Причина - <b>%{customdata[1]}</b><br>' +
            'Начало - <b>%{customdata[2]|%H:%M:%S (%d %b %Y)}</b><br>' +
            'Длительность - <b>%{customdata[3]:,.2f}</b> мин.<br><br>' +
            'Сменный день - <b>%{customdata[4]|%d %b %Y}</b><br>' +
            'Смена - <b>%{customdata[5]}</b><br>' +
            'Оператор - <b>%{customdata[6]}</b>'
        ),
    ).update_layout(
        yaxis_title="",
        title={
            'font': dict(size=25),
            'x': 0.5,
            'y': 0.85
        },
        showlegend=False,
        plot_bgcolor="#fff",
    )

    return figure


def show_gantt_chart():
    return dmc.Col([
        dmc.Card([
            Div(
                Graph(
                    figure=create_gantt_chart(),
                    id='output'
                ),
            )
        ])
    ])


def get_layout():
    return Div(
        dmc.Paper(
            dmc.Grid([
                show_general_info(),
                show_pie_chart(),
                show_gantt_chart()
            ], gutter='xl')
        )
    )


app.layout = get_layout()


@app.callback(
    Output('output', 'figure'),
    [State('selected_filter', 'value')],
    [Input('filter_button', 'n_clicks')],
    prevent_initial_call=True,
)
def update_card3(value, click):
    if click is None:
        raise PreventUpdate

    figure = create_gantt_chart()
    if value:
        for dat in figure.data:
            dat['marker']['opacity'] = 1 if dat['name'] in value else 0.3
    return figure


if __name__ == '__main__':
    app.run_server(debug=True)
