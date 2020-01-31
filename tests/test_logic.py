from flattree.logic import flatkey_to_keylist, keylist_to_flatkey
from flattree.logic import genleaves, unflatten, desparse


def test_flatkey_keylist():
    for fk in (None, 0, '', ' ', '_', '$', 'one_two_three'):
        kl = flatkey_to_keylist(fk, sep='_', esc='$')
        refk = keylist_to_flatkey(kl, sep='_', esc='$')
        assert refk == str(fk) if fk is not None else refk is None


def test_flattening_sequence_01(t0, t1):
    ft01 = dict(genleaves(t0, t1, sep='_', esc='$', idxbase=10))
    assert '$_$$__10_' in ft01
    assert ft01['menu_'] == 'Top'
    assert ft01['menu_items_12'] is None
    t01 = unflatten(ft01, sep='_', esc='$')
    t01mi = t01['menu']['items']
    assert isinstance(t01mi, dict)
    assert 12 in t01mi
    dt01T = desparse(t01, reindex=True)
    dt01mi = dt01T['menu']['items']
    assert dt01T['_$_'][1] == {}
    assert '_hide' not in dt01mi
    assert len(dt01mi) == 3
    dt01F = desparse(t01, reindex=False)
    assert len(dt01F['menu']['items']) == 13
    assert dt01T['_$_'] == t1['_$_']


def test_flattening_sequence_10(t0, t1):
    ft10 = dict(genleaves(t1, t0, sep='_', esc='$', idxbase=10))
    assert 'menu_items_12' not in ft10
    assert ft10['menu_'] == 'Bottom'
    assert ft10['menu_items_$_hide_12'] == 7
    t10 = unflatten(ft10, sep='_', esc='$')
    dt10T = desparse(t10, reindex=True)
    assert dt10T == t1
