# removing macros

- [x] remove macro related fields in Session
- [x] remove macro options in ScriptsListwidget
- [x] backup `MacroScript.py` and `MacroNodesTypes.py` in Ryven `macros` package
- [x] delete `Macroscript.py`, `MacroNodeTypes.py`
- [x] check `__init__.py` files
- [x] check `Script.py`
- [x] check for remaining 'macro' occurrences

# cleanups

- [x] packages in `setup.py`

# compilable core

- [x] implement signaling system with minimal interface in `ryvencore`
- [ ] ~~implement translation system in `ryvencore-qt` to convert those into qt signals~~
- [X] subclass `ryvencore.Session` in `ryvencore-qt` and expose in `ryvencore_qt.__init__`
- [ ] subclass `ryvencore.Node` in `ryvencore-qt` and expose in `ryvencore_qt.__init__`
- [ ] remove all `Session.CLASSES` dependencies in the core (maybe just keep it in the rcqt Session?)

# release notes

- change all `set_state(self, data)` to `set_state(self, data, version)`
- add version tags to your nodes
- add tag lists to your nodes
- load, repair, save and verify your projects
- macros?