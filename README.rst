=================
Siralim Dataminer
=================

A tool for parsing Siralim 3 data files and organizing them into a more usable format, namely a Python dictionary of creatures.

Requires extracted files to be in the ``./db`` directory.

Currently reads:

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