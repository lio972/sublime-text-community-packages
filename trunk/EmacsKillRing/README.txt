If you've used emacs, you may be used to a text-manipulation system that is very different from windows cut-and-paste. This is the emacs kill ring, and if you are like me, you miss the ability to hit ctrl+k to kill lines, ctrl+y to yank text back, ctrl+space to set a mark, and ctrl+w to cut a region to the kill buffer.

This package is for you; it implements these emacs commands;

- kill-line (ctrl+k)
- yank (ctrl+y)
- set-mark-command (ctrl+space)
- kill-region (ctrl+w)
- kill-ring-save (alt+w)

These are bound in Sublime Text to the same keys used by a default install of emacs.

This is tightly integrated with the windows clipboard; the most-recent cut is copied to the windows clipboard, and yank is really just paste, remapped. 

Additionally, there is another command in the package I'll call `yank-any`, which lets you yank any item in the kill ring.

These mapping overwrite singleSelection (ctrl+k) and redo (ctrl+y) so I've remapped them;

ctrl+shift+k is the new mapping for singleSelection, which was previously mapped to ctrl+k

ctrl+shift+z is the new mapping for redo, which was previously mapped to ctrl+y
