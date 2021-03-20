from setuptools import setup



setup(
    name='ryvencore-qt',
    version='0.0.0',
    license='LGPLv3',
    description='Python Library for building Visual Scripting Editors with Qt',
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
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires='>=3.8',
    install_requires=['PySide2'],
)
