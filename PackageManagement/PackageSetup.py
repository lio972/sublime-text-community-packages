#!/usr/bin/env python
#coding: utf8
#################################### IMPORTS ###################################

# Std Libs

from __future__ import with_statement

import glob
import shutil
import zipfile
import os.path
import logging

#################################### README ####################################
"""

PackageSetup
------------
Manages `Sublime Text` Package ( xxxx.sublime-package ) upgrades / removals

Terms
-----

`Pristine Packages`:

    Store pristine (untouched) copies of an xxxx.sublime-package for later
    purpose of determining difference between new and old packages.

`Installed Packages`:
    The folder where Sublime will place `double-clicked` sublime-package files.
    The package downloader from the PackageManagement plugin will also place
    packages in here.

    Typically `$APPDATA/Sublime Text/Installed Packages`
    Can be found with API call `sublime.installedPackagesPath()`

`Data Directory`:
    The folder where Sublime stores the uncompressed package files and users
    generally makes modifications.

    Typically $APPDATA/Sublime Text/Packages
    Can be found with API call `sublime.packagesPath()`

`Orphans`:
    Orphans are files that were in the old version of a package but no longer
    in the new version.

    These files may have been modified by the user and if so need to be backed
    up before deletion.

"""
###################################### LOG #####################################
"""

Log all file operations here so once plugins are loaded they can run merge tools

Kept in form of an easily consumed dict `upgradeLog`.

"""

upgradeLog = {'conflicts':[]}

def logConflict(fname):
    upgradeLog['conflicts'].append(fname)

# TODO:
    # informative logs

#################################### HELPERS ###################################

def isFileEntry(s):
    return s[-1] != '/'

def readFile(fname):
    with open(fname, 'rb') as f:
        return f.read()

def remove(fname):
    backupFileIfExists(fname)
    os.remove(fname)

def backupName(f, ext):
    # "Keep original extension rather than use xxx.py.bak (syntax support)"
    # f, orig_ext = os.path.splitext(f)
    return  f + '.' + ext #+ orig_ext

def backupFileIfExists(fname, ext='bak'):
    if os.path.exists(fname):
        logConflict(fname)
        backup = backupName(fname, ext)
        shutil.copy(fname, backup)

def writeFile(fname, data, backup=True):
    """

    Log all data

    """

    if backup:
        backupFileIfExists(fname)

    with open(fname, 'wb') as fo:
        fo.write(data)

def mkdirs(path):
    try:
        os.makedirs(path)
    except os.error:
        pass

############################# ADD / UPGRADE PACKAGE ############################

def upgradeArchive(new, old, pkgdir):
    """

       new:   new *.sublime-package zip file
       old:   old *.sublime-package zip file

    pkgdir:   uncompressed package directory

    """

    mkdirs(pkgdir)
    mkdirs(os.path.dirname(old))

    newar = zipfile.ZipFile(new)
    newfiles = set(filter(isFileEntry, newar.namelist()))

    oldar = None
    oldfiles = set()
    try:
        oldar = zipfile.ZipFile(old)
        oldfiles = set(filter(isFileEntry, oldar.namelist()))
    except (zipfile.error, IOError):
        pass

    # delete any orphaned files
    orphanedFiles = oldfiles - newfiles
    for f in orphanedFiles:
        try:
            fname = os.path.join(pkgdir, f)
            print 'deleting orphan file', fname

            remove(fname)
        except os.error:
            pass

    # extract any new files ( or files that have been deleted by user )
    for f in newfiles -  set( f for f in oldfiles if
                              os.path.exists(os.path.join(pkgdir, f)) ):

        fname = os.path.join(pkgdir, f)
        mkdirs(os.path.dirname(fname))
        print 'extracting `new` file', fname

        # Files may be considered `new` even if there is already an existing
        # file ( eg a version control checkout ) so make a backup
        writeFile(fname, newar.read(f), backup=True)

    # Remove the old archive, so we won't try and merge anything twice incase
    # we get a failure below
    try:
        os.remove(old)
    except os.error:
        pass

    # upgrade each file.
    for f in oldfiles & newfiles:
        fname = os.path.join(pkgdir, f)
        orig = oldar.read(f)
        newf = newar.read(f)

        if newf != orig:
            if os.path.exists(fname) and open(fname, 'rb').read() != orig:
                # Write common ancestor to file for easy 3 way merge.
                writeFile(
                    backupName(fname, ext='parent'),
                    orig, backup=False)

            print 'upgrading file', fname

            writeFile(fname, newf, backup=True)

    # The new now becomes the `old` in place for next update
    shutil.copy(new, old)

################################ REMOVE PACKAGE ################################

def removeArchive(old, pkgdir):
    oldar = None
    oldfiles = set()
    try:
        oldar = zipfile.ZipFile(old)
        oldfiles = set(filter(isFileEntry, oldar.namelist()))
    except (zipfile.error, IOError):
        pass
    oldar.close()

    # delete any orphaned files from pkgdir
    orphanedFiles = oldfiles
    for f in orphanedFiles:
        try:
            os.remove(os.path.join(pkgdir, f))
        except os.error:
            pass

    # delete the archive and destination
    try:
        os.remove(old)
    except os.error:
        pass

    try:
        os.rmdir(pkgdir)
    except os.error:
        pass

def pkgNewer(new, old):
    try:
        return (os.path.getmtime(new) > os.path.getmtime(old)
            or os.path.getsize(new) != os.path.getsize(old))
    except os.error:
        return True

def upgradePackageIfNew(package, pristinedir, datadir):
    oldPackage = os.path.join(pristinedir, os.path.basename(package))

    # if the zip is different from the one in pristinedir
    if pkgNewer(package, oldPackage):
        (base, ext) = os.path.splitext(os.path.basename(package))
        upgradeArchive(package, oldPackage, os.path.join(datadir, base))

################################## ENTRY POINT #################################

def upgrade(appdir, userdir, pristinedir, datadir):
    """

    This is the main() entry point Sublime comes into during (every) startup.

    # New incoming packages:

    appdir        $INSTALL_DIR\Pristine Packages
    userdir       $APPDATA\SublimeText\Installed Packages

                    * sublime.installedPackagesPath()

    # Old outgoing packages: eventual destination of new packages

    pristinedir   $APPDATA\SublimeText\Pristine Packages
    datadir       $APPDATA\SublimeText\Packages

                    * sublime.packagesPath()
    """

    # Look for sublime-package zip files
    packages = ( glob.glob(appdir +  "/*.sublime-package") +
                 glob.glob(userdir + "/*.sublime-package") )

    # Upgrade each package
    for pkg in packages:
        upgradePackageIfNew(pkg, pristinedir, datadir)

    # Delete any packages that are no longer around
    deprecatedPackages = (
        set([ os.path.basename(x) for x in
              glob.glob(pristinedir + "/*.sublime-package") ])  -

        set([ os.path.basename(x) for x in packages ]) )

    # Deprecated Zips
    for deprecated in deprecatedPackages:
        pristineZip = os.path.join(pristinedir, deprecated)
        (base, ext) = os.path.splitext(deprecated)

        removeArchive(pristineZip, os.path.join(datadir, base))

################################################################################