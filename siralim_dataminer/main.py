import functools
import json
import os
import re

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
    "Breeding": re.compile(
        r"AddBreedingCombo\(\d+, (?P<offspring>\d+), (?P<pedigree>.+), (?P<mate>.+)\)"
    ),
}


def get_db_contents(which):
    filename = get_data("filename")
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
    entry = get_data("creature")
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
            creatures[match["dbid"]][ckey] = match["lore"]

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


def update_breeding(creatures):
    for match in re.finditer(regexes["Breeding"], get_db_contents("Breeding")):
        # the first time we see an offspring, it needs a combo list created
        if "breeding" not in creatures[match["offspring"]]:
            creatures[match["offspring"]]["breeding"] = []

        # add this combo (pedigree and mate) to the offspring's combos
        creatures[match["offspring"]]["breeding"].append(
            {k: v.strip('"') for k, v in match.groupdict().items() if k != "offspring"}
        )


def prettify(creatures):
    condition_subs = get_data("condition_subs")
    for c in creatures:
        if "scr_con" in creatures[c]["trait"]["desc"]:
            # replace mangled condition references
            # with the condition's actual name
            creatures[c]["trait"]["desc"] = re.sub(
                r'"\)*? \+ scr_con\(obj_(.+?)\)\) \+ "',
                lambda match: condition_subs[match[1]],
                creatures[c]["trait"]["desc"],
            )
        if "scr_GetPassiveName" in creatures[c]["trait"]["desc"]:
            # GetPassiveName takes a dbid
            # so use that dbid in our own lookup
            creatures[c]["trait"]["desc"] = re.sub(
                r'"\)*? \+ scr_GetPassiveName\((\d+?)\)\) \+ "',
                lambda match: [
                    c["trait"]["name"]
                    for c in creatures.values()
                    if c["dbid"] == match[1]
                ][0],
                creatures[c]["trait"]["desc"],
            )


@functools.lru_cache()
def read_data():
    with open("data.json") as f:
        data = json.load(f)
    return data


def get_data(name):
    return read_data()[name]

