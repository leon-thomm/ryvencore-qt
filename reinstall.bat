pip uninstall --yes ryvencore-qt
rmdir /s /q build
rmdir /s /q dist
rmdir /s /q ryvencore_qt.egg-info
python setup.py install