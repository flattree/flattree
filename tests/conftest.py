import pytest


@pytest.fixture()
def t0():
    return {
        'menu': {
            '': 'Top',
            'items': [
                {'id': 'new', 'label': 'New...'},
                {'id': 'Help'},
                None
            ]
        }
    }


@pytest.fixture()
def t1():
    return {
        'menu': {
            '': 'Bottom',
            'items': {
                '_hide': [1, 3, 7]
            },
            'opt': {}
        },
        '_$_': [{'': []}, {}]
    }
