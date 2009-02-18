This is an implementation of the emacs kill ring, for Sublime Text.

To use it;

- ctrl+k is kill-line
- ctrl+y is yank
- ctrl+shift+y is yankChoice -- ie, choose from a list of all the entries in the kill ring

These mapping overwrite singleSelection (ctrl+k) and redo (ctrl+y) so I've remapped them;

- ctrl+shift+k is the new mapping for singleSelection, which was previously mapped to ctrl+k
- ctrl+shift+z is the new mapping for redo, which was previously mapped to ctrl+y
