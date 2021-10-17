# removing macros

- [x] remove macro related fields in Session
- [x] remove macro options in ScriptsListwidget
- [x] backup `MacroScript.py` and `MacroNodesTypes.py` in Ryven `macros` package
- [x] delete `Macroscript.py`, `MacroNodeTypes.py`
- [x] check `__init__.py` files
- [x] check `Script.py`
- [x] check for remaining 'macro' occurrences

# release notes

- change all `set_state(self, data)` to `set_state(self, data, version)`
- add version tags to your nodes
- add tag lists to your nodes
- load, repair, save and verify your projects
- macros?