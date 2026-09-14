import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import pc_monitor_agent as m

def test_demo_contract():
    m.DEMO = True
    d = m.collect()
    assert d['demo'] is True
    assert d['connection'] == 'DEMO'
    assert 'cpu' in d and 'ram' in d and 'network' in d
    assert d['gpu']['hotspot']['status'] == 'unavailable'

def test_unavailable_is_explicit():
    x = m.unavailable()
    assert x['value'] is None
    assert x['status'] == 'unavailable'
