import re

import pytest
from siralim_dataminer import __version__
from siralim_dataminer.main import (get_creatures, get_db_contents, name2key,
                                    regexes, update_cards, update_creatures)


def test_version():
    assert __version__ == '0.1.0'


@pytest.mark.parametrize("which,regex", regexes.items())
def test_regexes(which, regex):
    assert re.findall(regex, get_db_contents(which))


@pytest.fixture
def creatures():
    return get_creatures()


@pytest.mark.parametrize("name,key", name2key.items())
def test_update_creatures(creatures, name, key):
    update_creatures(creatures, name)
    for c in creatures.values():
        assert key in c


def test_update_cards(creatures):
    update_cards(creatures)
    for c in creatures.values():
        assert "card" in c
