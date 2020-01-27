import os
import re

filename = {
    "dir": "db",
    "prefix": "gml_Script_scr_",
    "suffix": ".gml",
}

name2key = {"Passives": "trait", "Materials": "material", "Lore": "lore"}

regexes = {
    "Passives": re.compile(
        r".*p = (?P<dbid>\d+)\n"
        r'.*\[p, 0\] = "(?P<name>.+)"\n'
        r'.*\[p, 1\] = .*?"(?P<desc>.+)"'  # there might be extra parentheses for buff/debuff references; ignore them
    ),
    "Materials": re.compile(
        r'.*\[mid, 0\] = "(?P<name>.+)"\n'
        r".*\[mid, 1\] = 2\n"  # only legendary materials
        r"(?:.*\n)*?"  # match & discard line(s?) in between
        r".*\[mid, 3\] = (?P<dbid>\d+)"
    ),
    "Lore": re.compile(r'case (?P<dbid>\d+):\s*return "(?P<lore>.*)";'),
}


def get_db_contents(which):
    if which == "Lore":
        kind = "Creature"
    else:
        kind = "Database"
    path = os.path.join(
        filename["dir"], "".join([filename["prefix"], kind, which, filename["suffix"]])
    )
    with open(path) as f:
        return f.read()


def get_creatures():
    entry = {
        "name": 7,
        "class": 2,
        "race": 11,
        "hp": 4,
        "mana": 6,
        "atk": 0,
        "int": 3,
        "def": 5,
        "spd": 12,
        "tags": 14,
        "dbid": 10,
    }

    fields = entry.keys()
    contents = get_db_contents("Creature")
    ids = re.findall(r"critconstant = (\d*)", contents)
    entries = [
        (
            result.strip('"')  # strings will have extra quotes
            for result in re.findall(
                r"\[critconstant, {0}\] = (.*)".format(entry[field]), contents
            )
        )
        for field in fields
    ]
    # 1. transpose data so we have a list of creature entries
    # 2. match the entry data to our fields and make those pairs into a dict
    # 3. finally make a dict with ids as keys and entries as values
    # example: {'180': {'name': 'Unicorn Vivifier', 'class': 'Life', 'race': 'Unicorn', 'hp': '31', 'mana': '31', 'atk': '11', 'int': '16', 'def': '16', 'spd': '16', 'tags': 'HORSE,HORN,HOLY'}}
    return dict(zip(ids, [dict(zip(fields, entry)) for entry in zip(*entries)]))


def update_creatures(creatures, which):
    """Parses a database and adds the data to a dict of creatures.
    @creatures: the dict returned from get_creatures.
    @which: the database to parse."""

    regex = regexes[which]
    ckey = name2key[which]

    if "dbid" not in regex.groupindex:
        raise re.error("regex must match dbid group", regex)
    if regex.groups < 2:
        raise re.error("regex must match something in addition to dbid", regex)

    matches = re.finditer(regex, get_db_contents(which))

    if which == "Lore":
        # dbid == cid
        for match in matches:
            groups = match.groupdict()
            creatures[groups["dbid"]][ckey] = groups["lore"]

    else:
        info = {}
        for match in matches:
            groups = match.groupdict()
            dbid = groups.pop("dbid")

            if regex.groups == 2:
                info[dbid] = groups.popitem()[1]  # get the other item's value
            elif regex.groups > 2:
                info[dbid] = groups

        for cid in creatures:
            # not every creature has a material
            creatures[cid][ckey] = info.get(creatures[cid]["dbid"])


def update_cards(creatures):
    # the logic is different enough that this gets its own function
    cid_re = re.compile(r"\d+")
    desc_re = re.compile(r'(?<=").+(?=")')  # don't capture quotes
    desc = None
    for line in get_db_contents("Cards").splitlines():
        if "str =" in line:
            desc = re.search(desc_re, line).group()
        elif "= str" in line:
            cid = re.search(cid_re, line).group()
            creatures[cid]["card"] = desc  # last desc set
        else:  # unique card effect
            cid = re.search(cid_re, line).group()
            creatures[cid]["card"] = re.search(desc_re, line).group()


def prettify(creatures):
    # TODO: strip('"')
    # TODO: resolve buff/debuff names
    pass
