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

def test_flattree_basics(configtree):
    ft = FlatTree(dict(x=0))
    assert ft.tree == {'x': 0}
    ft = FlatTree(ft, dict(x=1, y=dict(a=11, b=None)))
    assert ft.tree == {'x': 0, 'y': {'a': 11, 'b': None}}
    ft['y.b'] = 12
    assert ft.tree == {'x': 0, 'y': {'a': 11, 'b': 12}}
    assert ft['y.a'] == 11
    assert ft['y.b'] == 12
    assert ft['y.b.absent'] is None
    assert ft.get('y.b.absent', 'Absent') is 'Absent'
    del ft['y.a']
    assert ft['y.a'] is None
    ft['y.a'] = configtree
    branchkey = 'COMMON.sequence.start'
    assert 'y.a.' + branchkey in ft
    assert ft['y.a.' + branchkey] == 101
    ft.tree = configtree
    assert branchkey in ft
    assert ft[branchkey] == 101
    assert ft['x'] is None
    assert ft['y'] is None

def test_flattree_config(configtree, configfallback):
    prd_dict = configtree.get('production')
    dev_dict = configtree.get('development')
    common_dict = configtree.get('COMMON')
    prd_cfg = FlatTree(prd_dict, common_dict, configfallback)
    dev_cfg = FlatTree(dev_dict, common_dict, configfallback)
    one = prd_cfg['digits.one']
    assert one == configfallback.get('digits').get('one')
    assert one == dev_cfg['digits.one']
    assert dev_cfg['digits.nodigit'] is None
    assert prd_cfg['digits.nodigit'] is None
    assert prd_cfg.get('digits.nodigit', 0) == 0
    prd_start = prd_cfg['sequence.start']
    assert prd_start == configtree.get('COMMON').get('sequence').get('start')
    dev_start = dev_cfg['sequence.start']
    assert prd_start is dev_start
    prd_finish = prd_cfg['sequence.finish']
    dev_finish = dev_cfg['sequence.finish']
    assert prd_finish > dev_finish


def test_flattree_aliases(configtree, configfallback):
    prd_dict = configtree.get('production')
    common_dict = configtree.get('COMMON')
    prd_cfg = FlatTree(prd_dict, common_dict, configfallback,
                       aliases={'ONE': 'digits.one'})
    one = prd_cfg['ONE']
    assert one == configfallback.get('digits').get('one')
    prd_cfg.update_aliases({'--': 'digits.nodigit'})
    assert prd_cfg['--'] is None
    assert prd_cfg.get('--', 0) == 0
    prd_cfg.update_aliases({'SEQ': 'sequence'})
    assert prd_cfg['SEQ']['finish'] > prd_cfg['SEQ']['start']
    del prd_cfg['SEQ']
    assert prd_cfg.tree == {'digits': {'one': 1}}
    prd_cfg['SEQ'] = dict(start=0)
    del prd_cfg['ONE']
    assert prd_cfg.tree == {'sequence': {'start': 0}}


def test_flattree_default(configtree):
    ft = FlatTree(configtree, default='No value')
    assert ft['nonexistent'] is 'No value'


def test_flattree_keyerror(configtree):
    ft = FlatTree(configtree, raise_key_error=True)
    with pytest.raises(KeyError, match=r"nonexistent"):
        ft['nonexistent']
