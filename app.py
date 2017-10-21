# -*- coding: utf-8 -*-

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas

from figures import (
    binary_correlation_scatter, correlation_scatter, single_scatter
)
from utils import (
    compute_indicator_correlations, get_indicator_names, to_float
)

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
indicator_names = get_indicator_names(indicators)


title = 'NFHS-4 EDA'
app = dash.Dash()
app.title = title

LEVELS = ['state', 'district']

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
        figure = binary_correlation_scatter(nfhs_state_wise, x, y)

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
    return correlation_scatter(data, indicator)


if __name__ == '__main__':
    app.run_server(debug=True)
