Readme
======

This package helps with editing/navigating to Package files (keybindings/snippets etc)

Apologies, but documentation is in progress ;)

For the moment:

* Check out this [screencast][]
* Also this [one][]
* Browse this [forum thread][]
* And this [thread also][]
* Also this [one][]

[screencast]: http://blogdata.akalias.net/edit-preferences/edit-preferences.htm
[one]: http://blogdata.akalias.net/namespace-escaped-key-combo/namespace-escaped-key-combo.htm
[forum thread]: http://www.sublimetext.com/forum/viewtopic.php?f=4&t=220
[thread also]: http://www.sublimetext.com/forum/viewtopic.php?f=5&t=257
[one]: http://www.sublimetext.com/forum/viewtopic.php?f=4&t=531

Dependencies
============

*   AAALoadFirstExtensions ( >= 06/28/09 )

Changes
=======

06/28/09
--------

*   Documented dependency on AAALoadFirstExtensions
*   Now uses lxml for element.sourceline ( jump to binding to edit )
*   Includes `insertBindingRepr` command and &lt;bindings&gt;
*   Normalises sequencing of key combos for use of `insertBindingRepr` in the
    quickpanel ( eg alt+shift+t normalizes to ctrl+shift+t )
*   Normalises x,y,z,tab bindings to xyz&lt;tab&gt; for easy typing
*   Sorts key list by scope ( where possible )