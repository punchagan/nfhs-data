# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""Utility functions used by the code in the app."""

import pandas

NAN_VALUES = {'', '*', 'na', '#VALUE!'}


def compute_indicator_correlations(data, indicator, level, indicators):
    X = get_indicator_values(data, indicator, level)
    indicator_names = get_indicator_names(indicators)
    correlations = [
        X.corrwith(get_indicator_values(data, other, level))
        for other in indicators
    ]
    correlations = pandas.DataFrame(correlations, index=indicator_names)
    return correlations


def get_indicators(data):
    indicators = set(
        data.apply(
            lambda x: (x.indicator_id, x.indicator_category, x.indicator_name),
            axis=1
        ).unique()
    )
    # FIXME: Clean up data directly?
    try:
        indicators.remove(('#VALUE!', '#VALUE!', '#VALUE!'))
        indicators.remove(('23', pandas.np.nan, pandas.np.nan))
    except KeyError:
        pass
    indicators = sorted(indicators, key=lambda x: int(x[0]))
    return indicators


def get_indicator_names(indicators):
    return ['{} :: {}'.format(*i[1:]) for i in indicators]


def get_indicator_values(data, indicator, level='state', columns=None):
    """Return a data-frame with the specified columns for the indicator."""
    if columns is None:
        columns = ['rural', 'urban', 'total']

    indicator_id, _, _ = indicator
    X = data[data['indicator_id'] == indicator_id]
    X_ = X[columns]
    X_.index = X[level]
    # NOTE: WB data appears twice
    return X_[:-1] if level == 'state' else X_


def read_nfhs_csv(path):
    """Read NFHS data csv from the given path."""
    data = pandas.read_csv(
        path,
        dtype={'indicator_id': str, 'indicator_number': str},
        converters={'rural': to_float, 'urban': to_float, 'total': to_float},
        encoding='latin-1',
    )
    data.columns = data.columns.map(
        lambda x: 'indicator_id' if x == 'indicator_number' else x
    ).map(
        lambda x: 'indicator_name' if x == 'indicator' else x
    )
    return data


def to_float(x):
    """Pandas csv reader converter for float values."""
    x_ = x.replace(',', '').strip()
    return float(x_) if x_ not in NAN_VALUES else pandas.np.nan
