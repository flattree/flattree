import pytest

t0 = {
    'menu': {
        '': 'Top',
        'items': [
            {'id': 'new', 'label': 'New...'},
            {'id': 'Help'},
            None
        ]
    }
}

t1 = {
    'menu': {
        '': 'Bottom',
        'items': {
            '_hide': [1, 3, 7]
        },
        'opt': {}
    },
    '_$_': [{'': []}, {}]
}


@pytest.fixture(name='t0')
def t0_fixture():
    return t0


@pytest.fixture(name='t1')
def t1_fixture():
    return t1
