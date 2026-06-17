.. |pypi_download| image:: https://img.shields.io/pypi/dm/trame-code

==============================
trame-code |pypi_download|
==============================

Widget for Monaco VS code editor for trame

The editor can surface language features (autocomplete and hover
documentation) from your own server-side callbacks: pass ``completion``
and ``hover`` callables to the widget. The example below shows Python/VTK
completion and a hover docstring driven entirely from those callbacks.

.. image:: https://raw.githubusercontent.com/Kitware/trame-code/master/docs/completion-hover.png
   :alt: Monaco editor showing Python/VTK completion and a hover docstring
   :align: center


License
-----------------------------------------------------------

This library is distributed under the MIT License (Same as monaco/vscode-editor)


Development
-----------------------------------------------------------

Build and install the Vue components

.. code-block:: console

    cd vue-components
    npm i
    npm run build
    cd -

Install the python library

.. code-block:: console

    pip install -e .


JavaScript dependency
-----------------------------------------------------------

This Python package bundle the following set of libraries:

* ``monaco-editor@0.37.1``
* ``vscode-oniguruma@1.7.0``
* ``vscode-textmate@9.0.0``

If you would like us to upgrade any of those dependencies, `please reach out <https://www.kitware.com/trame/>`_.
