This is an implementation of the emacs kill ring, for Sublime Text.

Rather than explain the emacs kill ring, I'm assuming you're interested because you're moving from emacs, and already know what the kill ring is. 

You can use ctrl+k to do exactly what emacs does; yanks until the end of a line, or the new line if your cursor is there. This builds up an entry in the kill ring, and also sets the windows clipboard to the killed text. 

ctrl+y Yank always pulls the windows clipboard.

ctrl+shift+y allows you to choose from everything in the kill ring, and includes the current windows clipboard. 

These mapping overwrite singleSelection (ctrl+k) and redo (ctrl+y) so I've remapped them;

ctrl+shift+k is the new mapping for singleSelection, which was previously mapped to ctrl+k

ctrl+shift+z is the new mapping for redo, which was previously mapped to ctrl+y
