"Automatic Backups" is a plugin by SteveCooper. 

When you edit text files (scripts, prose, whatever) you often find yourself wishing for an older version. Ever accidentally deleted a chunk from an important configuration file, or wished you could roll back a document a few hours? This plugin takes a copy of every file you save and copies it into a backup directory structure, ensuring that you never lose an old version of the file. 

Once installed, any file you save will be copied into your documents folder, eg `<My Documents>\Sublime Text Backups`. For example, if you change `c:\autoexec.bat`, you'll get a backup saved to:

{{{
`c:\Documents and Settings\yourUserName\Sublime Text Backups\c-drive\autoexec-2008-03-22-22-22-46.bat`
}}}

That end bit is the timestamp, so you can see when the file was edited.

If you want to back up your files somewhere other than your documents folder, you can add an option. To change where all backups are made, open the `Preferences` menu and choose `Preferences`. Then double-click `Application`, and add a line like this to the end of the file;

{{{
backupDir c:\my files\archive\
}}}

To see if it's working, open the console with the `View` | `Console` menu item. When you save a file, you should see a line like this, indicating that the file has been backed up;

{{{
Automatic backup: backing up to d:\backups\C-drive\Documents and Settings\steve\Application Data\Sublime Text\Packages\User\AutomaticBackupsPlugin-2008-03-22-22-22-46.py`}}}
