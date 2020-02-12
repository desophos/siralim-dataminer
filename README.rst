=================
Siralim Dataminer
=================

A tool for parsing Siralim 3 data files and organizing them into a more usable format, namely a Python dictionary of creatures.

Requires extracted scripts in ``./db`` and sprites in ``./spr_crits_battle``.

Currently reads:
----------------

========= ===============================
Data      File (``gml_Script_scr_*.gml``)
========= ===============================
Creatures DatabaseCreature
Traits    DatabasePassives
Materials DatabaseMaterials
Lore      CreatureLore
Cards     DatabaseCards
Breeding  DatabaseBreeding
========= ===============================


Notes on data.json:
-------------------

* filename: for referencing script files

* creature: structure of the creature database

* condition_ids: currently unused but seems important to have for future reference

* condition_subs:

  * the decompiler mangles ``scr_con`` calls for some reason; these are the objects it uses instead of ints
  * "Drunk" seems to only ever be referenced literally
