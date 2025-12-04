eyelid-builder
==============

Maya tool used to build an eyelid rig based on joints and crves

How To
--------
To launch the tool, run this inside maya:

```python
import sys
path = "path/to/eyelid-builder/src"
if path not in sys.path:
	sys.path.insert(0, path)
import eyelid_builder.ui as eyelid_ui
win = eyelid_ui.EyelidGui()
win.show()
```

Features
--------

* TODO

Generate sphinx documentation
-----------------------------
* build a venv
* ``python -m pip install sphinx``
* ``cd eyelid-builder``
* Optional - if you want to build auto-doc based on your docstrings, run ``sphinx-apidoc -o docs eyelid-builder``
* ``sphinx-build -b html .\docs\ .\docs\_build``


Launch tests
-----------------------------
* cd to the root of your project
* unix: ``mayapy -m pytest .\tests_eyelid_builder\``
* windows: ``& path/to/mayapy -m pytest .\tests_eyelid_builder\``


Help
-----------------------------
https://charlotte.lerat1991.gitlab.io/eyelid-builder


Credits
-------

