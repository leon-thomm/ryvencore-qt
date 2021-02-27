from setuptools import setup



setup(
    name='ryvencore-qt',
    version='0.0.0',
    license='MIT',
    description='Qt based library for making flow-based visual programming editors',
    author='Leon Thomm',
    author_email='l.thomm@mailbox.org',
    packages=[
        'ryvencore_qt',
        'ryvencore_qt.resources',

        'ryvencore_qt.src',
        'ryvencore_qt.src.conv_gui',
        'ryvencore_qt.src.node_selection_widget',

        'ryvencore_qt.src.ryvencore',
        'ryvencore_qt.src.ryvencore.logging',
        'ryvencore_qt.src.ryvencore.script_variables',
    ],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
    python_requires='>=3.8',
    install_requires=['PySide2'],
)
