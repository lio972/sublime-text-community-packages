@ECHO OFF

del PackageDownloader.sublime-package

set sevenzip="%ProgramFiles(x86)%\7-zip\7z.exe"
%sevenzip% A -tzip PackageDownloader.sublime-package @listOfFilesInPackage.txt

rem ren PackageDownloader.zip PackageDownloader.sublime-package
