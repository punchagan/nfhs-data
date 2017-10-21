# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""Utility functions used by the code in the app."""

import plotly.graph_objs as go

MARKERS = ['circle', 'square', 'diamond']


def binary_correlation_scatter(data, indicator_x, indicator_y, level='state'):
    """Scatter plot to view correlation between two indicators."""
    X = data[data['indicator_id'] == indicator_x]
    Y = data[data['indicator_id'] == indicator_y]
    text = (
        X[level] if level == 'state' else
        X.apply(lambda x: '{district}-{state}'.format(**x), axis=1)
    )

    scatter_data = [
        {
            'x': X[column],
            'y': Y[column],
            'text': text,
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
                'title': '{indicator_category} :: {indicator_name}'.format(**X.iloc[0]),
            },
            'yaxis': {
                'title': '{indicator_category} :: {indicator_name}'.format(**Y.iloc[0]),
            },
        }
    }
    return figure


def correlation_scatter(data, indicator):
    """Scatter plot to view correlation between an indicator and all others."""
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


def single_scatter(data, indicator_id):
    """Scatter plot of a single indicator data."""
    indicator_data = data[data['indicator_id'] == indicator_id]
    scatter_data = [
        {
            'x': indicator_data['state'],
            'y': indicator_data[column],
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
