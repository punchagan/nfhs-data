# -*- coding: utf-8 -*-

import os

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import flask

from figures import (
    binary_correlation_scatter, correlation_scatter, single_scatter
)
from utils import (
    compute_indicator_correlations, get_indicators, get_indicator_names,
    read_nfhs_csv,
)

DATA = {
    'state': {
        'data': read_nfhs_csv('nfhs_state-wise.csv')
    },
    'district': {
        'data': read_nfhs_csv('nfhs_district-wise.csv')
    }
}
TITLE = 'NFHS-4 EDA'
LEVELS = ['state', 'district']

server = flask.Flask('app')
server.secret_key = os.environ.get('secret_key', 'secret')

app = dash.Dash(name=TITLE, server=server)
app.title = TITLE

app.layout = html.Div(children=[
    html.H1(children=TITLE),
    dcc.Dropdown(
        id='level-dropdown',
        options=[
            {
                'label': '{} wise'.format(level.capitalize()),
                'value': level,
            }
            for level in LEVELS
        ],
        value=LEVELS[0],
    ),
    dcc.Dropdown(
        id='state-dropdown',
        placeholder='Select state',
        options=[],
        value=None,
    ),
    dcc.Dropdown(
        id='indicator-dropdown',
        options=[],
        value=[],
        multi=True,
    ),
    dcc.Graph(id='nfhs-graph'),
    dcc.Graph(id='nfhs-correlations-graph'),
])


@app.callback(Output('state-dropdown', 'disabled'),
              [Input('level-dropdown', 'value')])
def disable_state_selection(level):
    return True if level == 'state' else False


@app.callback(Output('indicator-dropdown', 'options'),
              [Input('level-dropdown', 'value')])
def update_indicator_options(level):
    if level not in DATA:
        return []

    data = DATA[level]
    if 'indicators' not in data:
        indicators = get_indicators(data['data'])
        indicator_names = get_indicator_names(indicators)
        data['indicator_options'] = [
            {'label': indicator_names[i], 'value': indicator[0]}
            for i, indicator in enumerate(indicators)
        ]
        data['indicators'] = indicators
    return data['indicator_options']


@app.callback(Output('state-dropdown', 'options'),
              [Input('level-dropdown', 'value')])
def update_state_options(level):
    if level == 'state':
        return []
    else:
        data = DATA[level]['data']
        states = data['state'].unique()
        return [
            {'label': state, 'value': state}
            for state in states
        ]


@app.callback(Output('nfhs-graph', 'figure'),
              [Input('level-dropdown', 'value'),
               Input('state-dropdown', 'value'),
               Input('indicator-dropdown', 'value')])
def update_indicator_graph(level, state, ids):
    data = DATA[level]['data']
    if level == 'district' and state is not None:
        data = data[data['state'] == state]

    if len(ids) == 1:
        indicator_id = ids[0]
        figure = single_scatter(data, indicator_id, level)

    elif len(ids) >= 2:
        x, y = ids[:2]
        figure = binary_correlation_scatter(data, x, y, level)

    else:
        figure = None

    return figure


@app.callback(Output('nfhs-correlations-graph', 'figure'),
              [Input('level-dropdown', 'value'),
               Input('state-dropdown', 'value'),
               Input('indicator-dropdown', 'value')])
def update_correlations_graph(level, state, ids):
    data = DATA[level]['data']
    if level == 'district' and state is not None:
        data = data[data['state'] == state]

    if 'indicators' not in DATA[level]:
        return None

    indicators = DATA[level]['indicators']
    if len(ids) == 1:
        indicator_id = ids[0]

    else:
        indicator_id = None

    if indicator_id is None:
        return None

    indicator = [i for i in indicators if i[0] == indicator_id][0]
    correlations = compute_indicator_correlations(data, indicator, level, indicators)
    return correlation_scatter(correlations, indicator)

if __name__ == '__main__':
    app.run_server(debug=True)
