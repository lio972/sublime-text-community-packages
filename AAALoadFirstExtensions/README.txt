Readme
======

This Package contains various plugin helpers, monkey-patches and 3rd Party Libs

A lot of plugins depend on this. If you aren't sure whether you need it, just get it.

Plugin helper modules:
----------------------

* pluginhelpers
* quickpanelcols
* tmscopes
* sublimeconstants
* indentation

3rd Party Libs:
---------------

These are all placed on sys.path with use of a GetShortPathName call.

*   lxml
*   comtypes
*   SendKeys
*   docutils
*   markdown
*   smartypants
*   Pyro
*   pywinauto

Patches
-------

*   sublime.activeWindow()
*   sublime.addOnLoadedCallback(view, cb)
*   sublime.addOnActivatedCallback(view, cb)

Changes
=======

07/12/09
--------

*   Added in indentation helpers

06/28/09
--------

*   Added in pluginhelpers/quickpanelcols/tmscopes/sublimeconstants
*   Added in lxml/comtypes/SendKeys/docutils/markdown/smartypants/Pyro/pywinauto