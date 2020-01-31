import pytest
from flattree import FlatTree


def test_flattree_weird_usage():
    ft = FlatTree()
    assert ft[None] is None
    assert ft.tree is None
    assert ft.data == {None: None}
    assert ft == FlatTree(None)
    ft = FlatTree(False)
    assert ft.tree is False
    assert ft.data == {None: False}
    ft = FlatTree(0)
    assert ft.tree == 0
    assert ft.data == {None: 0}
    ft = FlatTree(0, 1)
    assert ft.tree == 0
    assert ft.data == {None: 0}
    ft = FlatTree(0, 1, 2, root='')
    assert ft.data == ft.tree
    ft = FlatTree(0, 1, 2, root='.')
    assert ft.data == {'.': 0}
    assert ft.tree == {'': {'': 0}}
    ft = FlatTree(0, 1, 2, root='one.two')
    assert ft.tree == {'one': {'two': 0}}
    assert ft.data == {'one.two': 0}
    ft = FlatTree(0, 1, 2, root='one\\.two')
    assert ft.tree == {'one.two': 0}
    assert ft.data == {'one\\.two': 0}
    ft = FlatTree(0, 1, 2, root='one\\.two')
    assert ft.tree == {'one.two': 0}
    assert ft.data == {'one\\.two': 0}


def test_flattree_basics(t0, t1):
    ft = FlatTree([t0, t1], root='')
    assert ft['.1.menu.items._hide'] == [1, 3, 7]
    ft = FlatTree(t0, t1, root='')
    assert ft['.menu.items._hide'] is None
    assert ft.tree['']['menu']['opt'] == {}
    assert ft.tree['']['menu']['items'][1] == ft.unflatten('.menu.items.1')
    ft.tree = FlatTree(t1, root='')
    assert ft['.menu.items._hide'] == [1, 3, 7]


def test_flattree_del_set(t0, t1):
    ft = FlatTree(t0, t1)
    del ft['menu.items']
    assert sorted(list(ft.tree.keys())) == ['_$_', 'menu']
    ft['menu.items'] = [{'id': 'new', 'label': 'New...'}, {'id': 'Help'}]
    assert ft['menu.items.0.id'] == 'new'


def test_flattree_default(t0):
    ft = FlatTree(t0, default='No value')
    assert ft['nonexistent'] is 'No value'


def test_flattree_keyerror(t0):
    ft = FlatTree(t0, raise_key_error=True)
    with pytest.raises(KeyError, match=r"nonexistent"):
        return ft['nonexistent']


def test_flattree_alises(t0, t1):
    ft = FlatTree([t1, t0], default=-1)
    ft.update_aliases({0: '0.menu.items._hide.0', 2: '0.menu.items._hide.2'})
    assert type(ft[0]) is type({})  # key takes precedence over the alias
    assert ft[2] == 7
    ft.update_aliases({2: None})  # means "delete alias"
    assert ft[2] == -1  # default
