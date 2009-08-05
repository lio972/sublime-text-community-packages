This plugin is designed to provide an integrated interface to the most commonly used features of Mercurial.

# Easy Installation
Find the Mercurial package on http://sublimetextwiki.com, download it, and double click-it.

Sublime Text should recognize and install it.

After you double click it, restart Sublime Text.

This will give you keybindings for Commit, Add, Remove, and Diff actions.

# Manual Installation
Copy the "MercurialCommand.py" and "MercurialCommand.package-menu" files to your Packages\User folder:
	- On Vista, this is \Users\UserName\AppData\Roaming\Sublime Text\Packages\User\
	- On XP, this is \Documents and Settings\UserName\Application Data\Sublime Text\Packages\User\

Optionally, alter your "Default.sublime-keymap" file and create any shortcuts you wish. Some examples are provided with the plugin.

# Usage
There is a pull-down menu under Tools->Packages->Mercurial that provides access to all the commands provided by the plugin.

You may also map any of the Mercurial commands to a keystroke and use them in that way.

A thing to note is that this command uses the currently open buffer to determine the file path where the commands should be run from.

# Notes
When using the revert command, you must change to another open buffer or close 
and reopen the buffer in question. This is because Sublime Text needs to realize
that the file has been modified outside the editor so it can be reloaded.