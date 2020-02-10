import re

import pytest
from siralim_dataminer import __version__
from siralim_dataminer.main import (get_creatures, get_db_contents, name2key,
                                    prettify, regexes, update_breeding,
                                    update_cards, update_creatures)


def test_version():
    assert __version__ == "0.1.0"


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


def test_breeding(creatures):
    update_breeding(creatures)
    for c in creatures.values():
        if "breeding" in c:  # not all creatures have breeding combos
            assert len(c["breeding"]) > 0
            for combo in c["breeding"]:
                assert "pedigree" in combo and "mate" in combo, c

    # breeding combo 9
    assert {"pedigree": "561", "mate": "470"} in creatures["560"]["breeding"]
    # breeding combo 489
    assert {"pedigree": "Cerberus", "mate": "Cerberus"} in creatures["454"]["breeding"]
    # breeding combo 2471
    assert {"pedigree": "193", "mate": "Basilisk"} in creatures["195"]["breeding"]
    # breeding combo 2515
    assert {"pedigree": "Spectre", "mate": "6"} in creatures["441"]["breeding"]


def test_prettify(creatures):
    update_creatures(creatures, "Passives")
    prettify(creatures)
    for c in creatures.values():
        assert "scr_con" not in c["trait"]["desc"], c["trait"]
        assert "scr_GetPassiveName" not in c["trait"]["desc"], c["trait"]
        assert not any('"' in v for v in c["trait"].values()), c["trait"]
        assert not any('"' in v for v in c.values()), c
