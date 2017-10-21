# -*- coding: utf-8 -*-

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas
import plotly.graph_objs as go


NAN_VALUES = {'', '*', 'na'}


def to_float(x):
    x_ = x.replace(',', '').strip()
    return float(x_) if x_ not in NAN_VALUES else pandas.np.nan

nfhs_state_wise = pandas.read_csv(
    'nfhs_state-wise.csv',
    converters={'rural': to_float, 'urban': to_float, 'total': to_float}
)

indicators = set(
    nfhs_state_wise.apply(
        lambda x: (x.indicator_id, x.indicator_category, x.indicator),
        axis=1
    ).unique()
)
# FIXME: Clean up data directly?
indicators.remove(('#VALUE!', '#VALUE!', '#VALUE!'))
indicators.remove(('23', pandas.np.nan, pandas.np.nan))
indicators = sorted(indicators, key=lambda x: int(x[0]))
indicator_names = ['{} :: {}'.format(*i[1:]) for i in indicators]

MARKERS = ['circle', 'square', 'diamond']


title = 'NFHS-4 EDA'
app = dash.Dash()
app.title = title


def get_indicator_values(data, indicator):
    indicator_id, _, _ = indicator
    X = data[data['indicator_id'] == indicator_id]
    X_ = X[['rural', 'urban', 'total']]
    X_.index = X['state']
    return X_[:-1]  # FIXME: WB data appears twice


def compute_correlations(data, indicators):
    rural, urban, total = {}, {}, {}
    I = indicators
    for i, indicator in enumerate(I):
        print(i)
        correlations = compute_indicator_correlations(data, indicator, I)
        rural[indicator] = correlations['rural']
        urban[indicator] = correlations['urban']
        total[indicator] = correlations['total']

    rural = pandas.DataFrame(rural).sort_index()
    urban = pandas.DataFrame(urban).sort_index()
    total = pandas.DataFrame(total).sort_index()
    return rural, urban, total


def compute_indicator_correlations(data, indicator, indicators):
    X = get_indicator_values(data, indicator)
    correlations = [
        X.corrwith(get_indicator_values(data, other))
        for other in indicators
    ]
    correlations = pandas.DataFrame(correlations, index=indicator_names)
    return correlations


def single_correlation_scatter(data, indicator):
    scatter_data = [
        {
            'x': data[column].index,
            'y': data[column],
            'name': column.capitalize(),
            'mode': 'markers+lines',
            'marker': {'symbol': MARKERS[i % len(MARKERS)], 'size': 8},
        }
        for i, column in enumerate(('rural', 'urban', 'total'))
    ]

    figure = {
        'data': [go.Scatter(d) for d in scatter_data],
        'layout': {
            'title': '{}::{}'.format(*indicator[1:]),
            'height': 800,
            'width': 1900,
            'hovermode': 'closest',
            'xaxis': {
                'title': 'Indicators',
            },
            'yaxis': {
                'title': 'Correlation',
            },
        }
    }
    return figure


def single_scatter(data):
    scatter_data = [
        {
            'x': data['state'],
            'y': data[column],
            'name': column.capitalize(),
            'mode': 'markers+lines',
            'marker': {'symbol': MARKERS[i % len(MARKERS)], 'size': 8},
        }
        for i, column in enumerate(('rural', 'urban', 'total'))
    ]

    figure = {
        'data': [go.Scatter(d) for d in scatter_data],
        'layout': {
            'height': 800,
            'width': 900,
            'hovermode': 'closest',
            'xaxis': {
                'title': 'State',
            },
            'yaxis': {
                'title': 'Value',
            },
        }
    }
    return figure


def correlation_scatter(data, indicator_x, indicator_y):
    X = nfhs_state_wise[nfhs_state_wise['indicator_id'] == indicator_x]
    Y = nfhs_state_wise[nfhs_state_wise['indicator_id'] == indicator_y]

    scatter_data = [
        {
            'x': X[column],
            'y': Y[column],
            'text': X['state'],
            'name': column.capitalize(),
            'mode': 'markers',
            'marker': {'symbol': MARKERS[i % len(MARKERS)], 'size': 8},
        }
        for i, column in enumerate(('rural', 'urban', 'total'))
    ]

    figure = {
        'data': [go.Scatter(d) for d in scatter_data],
        'layout': {
            'height': 800,
            'width': 900,
            'hovermode': 'closest',
            'xaxis': {
                'title': '{indicator_category} :: {indicator}'.format(**X.iloc[0]),
            },
            'yaxis': {
                'title': '{indicator_category} :: {indicator}'.format(**Y.iloc[0]),
            },
        }
    }
    return figure


app.layout = html.Div(children=[
    html.H1(children=title),
    dcc.Dropdown(
        id='indicator-dropdown',
        options=[
            {
                'label': indicator_names[i],
                'value': indicator_id,
            }
            for i, (indicator_id, _, _) in enumerate(indicators)
        ],
        value=[indicators[0][0]],
        multi=True,
    ),
    dcc.Graph(id='nfhs-graph'),
    dcc.Graph(id='nfhs-correlations-graph'),
])

app.css.append_css({
    'external_url': "https://codepen.io/chriddyp/pen/bWLwgP.css"
})


@app.callback(Output('nfhs-graph', 'figure'),
              [Input('indicator-dropdown', 'value')])
def update_indicator_graph(ids):
    if len(ids) == 1:
        indicator_id = ids[0]
        data = nfhs_state_wise[nfhs_state_wise['indicator_id'] == indicator_id]
        figure = single_scatter(data)

    elif len(ids) >= 2:
        x, y = ids[:2]
        figure = correlation_scatter(nfhs_state_wise, x, y)

    else:
        figure = None

    return figure


@app.callback(Output('nfhs-correlations-graph', 'figure'),
              [Input('indicator-dropdown', 'value')])
def update_correlations_graph(ids):
    if len(ids) == 1:
        indicator_id = ids[0]

    else:
        indicator_id = None

    if indicator_id is None:
        return None

    indicator = [i for i in indicators if i[0] == indicator_id][0]

    data = compute_indicator_correlations(
        nfhs_state_wise, indicator, indicators
    )
    return single_correlation_scatter(data, indicator)


if __name__ == '__main__':
    app.run_server(debug=True)
