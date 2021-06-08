from setuptools import setup


long_descr_content = """
`rvencore-qt` is a library for building flow-based visual scripting editors for Python with Qt. It comes from the [Ryven](https://github.com/leon-thomm/Ryven) project. For more info see [GitHub](https://github.com/leon-thomm/ryvencore-qt).
"""


setup(
    name='ryvencore-qt',
    version='0.0.2.1',
    license='LGPLv2.1',
    description='Library for building Visual Scripting Editors with Qt',
    long_description=long_descr_content,
    long_description_content_type='text/markdown',
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
        'ryvencore_qt.src.ryvencore.dtypes',
    ],
    include_package_data=True,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires='>=3.6',
    install_requires=['PySide2', 'QtPy'],
)
