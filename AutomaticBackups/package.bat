IF EXIST AutomaticBackups.zip THEN del AutomaticBackups.zip
IF EXIST AutomaticBackups.sublime-package THEN del AutomaticBackups.sublime-package

"%ProgramFiles%\7-zip\7z.exe" A AutomaticBackups.zip @listOfFilesInPackage.txt

ren AutomaticBackups.zip AutomaticBackups.sublime-package
