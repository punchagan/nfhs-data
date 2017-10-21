# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""Utility functions used by the code in the app."""

import pandas

NAN_VALUES = {'', '*', 'na'}


def compute_indicator_correlations(data, indicator, indicators):
    X = get_indicator_values(data, indicator)
    indicator_names = get_indicator_names(indicators)
    correlations = [
        X.corrwith(get_indicator_values(data, other))
        for other in indicators
    ]
    correlations = pandas.DataFrame(correlations, index=indicator_names)
    return correlations


def get_indicator_names(indicators):
    return ['{} :: {}'.format(*i[1:]) for i in indicators]


def get_indicator_values(data, indicator, columns=None):
    """Return a data-frame with the specified columns for the indicator."""
    if columns is None:
        columns = ['rural', 'urban', 'total']

    indicator_id, _, _ = indicator
    X = data[data['indicator_id'] == indicator_id]
    X_ = X[columns]
    X_.index = X['state']
    # NOTE: WB data appears twice
    return X_[:-1]


def to_float(x):
    """Pandas csv reader converter for float values."""
    x_ = x.replace(',', '').strip()
    return float(x_) if x_ not in NAN_VALUES else pandas.np.nan
