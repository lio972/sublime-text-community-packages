# Pastie plugin

This plugin automates sending pastes to Pastie http://pastie.caboo.se/

Pastes are sent in a background thread so the command will not block sublime.

Usage
-----

ctrl+f12: send paste

ctrl+alt+f12: send private paste

IRC Client Activation
---------------------

Pastie is by default configured to activate Pidgin (win32api SetForegroundWindow) and then SendKeys the shortcut sequence for paste.

The IRC client activation is configurable though. It's just a matter of setting a few regexes to match your prefered IRC clients top level window and title text. eg "^#.*"

See instruction in the source ( pastie.py ). Be sure to temporarily disable posting pastes while testing IRC client activation.