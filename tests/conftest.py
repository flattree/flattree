import pytest

@pytest.fixture()
def configtree():
    return {
        'COMMON': {
            'sequence': {
                'start': 101
            }
        },
        'development': {
            'sequence': {
                'finish': 110
            }
        },
        'production': {
            'sequence': {
                'finish': 1000
            }
        }
    }

@pytest.fixture()
def configfallback():
    return {
        'digits': {
            'one': 1
        }
    }
