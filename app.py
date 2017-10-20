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
categories = set(nfhs_state_wise['indicator_category'].unique())
# FIXME: Clean up data directly?
categories.remove(pandas.np.nan)
categories.remove('#VALUE!')
categories = sorted(categories)

indicators = set(nfhs_state_wise['indicator'].unique())
# FIXME: Clean up data directly?
indicators.remove('#VALUE!')
indicators.remove(pandas.np.nan)
indicators = sorted(indicators)


def get_category(data, indicator):
    categories = data[data['indicator'] == indicator]['indicator_category']
    return categories.unique()[0]


i_c_map = {
    indicator: get_category(nfhs_state_wise, indicator)
    for indicator in indicators
}
indicators = sorted(indicators, key=lambda x: i_c_map[x])

MARKERS = ['circle', 'square', 'diamond']


title = 'NFHS-4 EDA'
app = dash.Dash()
app.title = title


def get_indicator_values(data, indicator):
    X = data[data['indicator'] == indicator]
    X_ = X[['rural', 'urban', 'total']]
    X_.index = X['state']
    return X_[:-1]  # FIXME: WB data appears twice


def compute_indicator_correlations(data, indicators):
    rural, urban, total = {}, {}, {}
    I = indicators
    for i, indicator in enumerate(I):
        print(i)
        X = get_indicator_values(data, indicator)
        correlations = [
            X.corrwith(get_indicator_values(data, other))
            for other in I
        ]
        correlations = pandas.DataFrame(correlations, index=I)
        rural[indicator] = correlations['rural']
        urban[indicator] = correlations['urban']
        total[indicator] = correlations['total']

    rural = pandas.DataFrame(rural).sort_index()
    urban = pandas.DataFrame(urban).sort_index()
    total = pandas.DataFrame(total).sort_index()
    return rural, urban, total


RURAL, URBAN, TOTAL = compute_indicator_correlations(
    nfhs_state_wise, indicators
)


def correlation_heatmap(data):
    figure = {
        'data': [
            go.Heatmap(z=data.values,
                       x=data.columns,
                       y=data.index)
        ],
        'layout': {
            'height': 800,
            'width': 900,
            'hovermode': 'closest',
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
    X = nfhs_state_wise[nfhs_state_wise['indicator'] == indicator_x]
    Y = nfhs_state_wise[nfhs_state_wise['indicator'] == indicator_y]

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
                'title': indicator_x,
            },
            'yaxis': {
                'title': indicator_y,
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
                'label': '%s :: %s' % (i_c_map[indicator], indicator),
                'value': indicator
            }
            for indicator in indicators
        ],
        value=indicators[0],
        multi=True,
    ),
    dcc.Graph(id='nfhs-graph'),
    dcc.Graph(id='nfhs-correlations-rural', figure=correlation_heatmap(RURAL)),
    dcc.Graph(id='nfhs-correlations-urban', figure=correlation_heatmap(URBAN)),
    dcc.Graph(id='nfhs-correlations-total', figure=correlation_heatmap(TOTAL)),
])

app.css.append_css({
    'external_url': "https://codepen.io/chriddyp/pen/bWLwgP.css"
})


def category_indicators(data, category=None):
    category_data = (
        data[data['indicator_category'] == category]
        if category is not None else data

    )
    return sorted(set(category_data['indicator']))


@app.callback(Output('nfhs-graph', 'figure'),
              [Input('indicator-dropdown', 'value')])
def update_graph(indicators):
    if isinstance(indicators, str):
        indicator = indicators
        data = nfhs_state_wise[nfhs_state_wise['indicator'] == indicator]
        figure = single_scatter(data)

    elif len(indicators) == 1:
        indicator = indicators[0]
        data = nfhs_state_wise[nfhs_state_wise['indicator'] == indicator]
        figure = single_scatter(data)

    elif len(indicators) >= 2:
        x, y = indicators[:2]
        figure = correlation_scatter(nfhs_state_wise, x, y)

    else:
        figure = None

    return figure


if __name__ == '__main__':
    app.run_server(debug=True)
