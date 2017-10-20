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

graphs = ['Single Indicator', 'Correlations']

app.layout = html.Div(children=[
    html.H1(children=title),
    dcc.Dropdown(
        id='category-dropdown',
        options=[
            {'label': category, 'value': category}
            for category in categories
        ],
        value=categories[0]
    ),
    dcc.Dropdown(
        id='indicator-dropdown',
        options=[],
        value=None,
    ),
    dcc.Graph(id='nfhs-graph')
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


@app.callback(Output('indicator-dropdown', 'options'),
              [Input('category-dropdown', 'value')])
def update_indicator_options(category):
    indicators = category_indicators(nfhs_state_wise, category)
    return [
        {'label': indicator, 'value': indicator}
        for indicator in indicators
    ]


@app.callback(Output('indicator-dropdown', 'value'),
              [Input('category-dropdown', 'value')])
def update_indicator_value(category):
    indicators = category_indicators(nfhs_state_wise, category)
    return indicators[0]


@app.callback(Output('nfhs-graph', 'figure'),
              [Input('category-dropdown', 'value'),
               Input('indicator-dropdown', 'value')])
def update_graph(category, value, column='total'):
    data = nfhs_state_wise[
        (nfhs_state_wise['indicator_category'] == category) &
        (nfhs_state_wise['indicator'] == value)
    ]
    return scatter(data)


def scatter(data):
    scatter_data = [
        {
            'x': data['state'],
            'y': data[column],
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
                'title': 'State',
            },
            'yaxis': {
                'title': 'Value',
            },
        }
    }
    return figure


if __name__ == '__main__':
    app.run_server(debug=True)
