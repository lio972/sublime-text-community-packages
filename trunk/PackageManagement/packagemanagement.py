#!/usr/bin/env python
#coding: utf8
#tabs: 2
#################################### IMPORTS ###################################

# Std Libs
import threading
import zipfile
import sys
import os
import shutil
import urllib
import random

from functools import partial
from os.path import join, exists

# Sublime Libs
import sublime
import sublimeplugin

from PackageSetup import upgradeArchive

from pluginhelpers import threaded, staggered
from quickpanelcols import format_for_display


# AppLibs
from mergeconflicts import notify as notify_of_conflicts_if_any

#################################### AUTHOR ####################################

__author__   =  "Steve Cooper & Nicholas Dudfield"
__version__  =  "0.1"

#################################### HELPERS ###################################

def getUrl(url):
    return urllib.urlopen(url).read()

def packageRoot():
    return "http://www.sublimetextwiki.com/sublime-packages/"

def listPackages():
    packageList = getUrl(packageRoot() + "all.sublime-distro")

    packageLines = [ l for l in packageList.split("\n") if l.strip() ]
    packageNames = sorted( os.path.splitext(line)[0] for line in packageLines )

    return packageNames

################################################################################

def description():
    return random.choice (
[ 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod',
  'tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,',
  'quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo',
  'consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse',
  'cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non',
  'proident, sunt in culpa qui officia deserunt mollit anim id est laborum.' ] )

def version():
    return "%s.%s" % (random.randint(0, 2), random.randint(0, 9))

class BrowsePackagesOnSublimeTextWiki(sublimeplugin.WindowCommand):
    def notify(self, packageNames):
        pkg_path = sublime.packagesPath()

        packages = sorted (
            ( exists(join(pkg_path,  pkg)), pkg ) for pkg in packageNames )

        display = format_for_display (
            [
                ( ( 'A' if not pkg_exists else 'U' ),
                  pkg,
                  # version(),
                  # description()
                )
                for  pkg_exists, pkg in packages
            ],
        )

        self.window.showQuickPanel (
            "",
            "packageSelectedForInstallation",
            [p[1] for p in packages],
            display)

    @threaded(finish=notify)
    def run(self, window, args):
        self.window = window
        sublime.setTimeout (
            lambda : sublime.statusMessage("Downloading Packages List"), 0)
        packageList = listPackages()

        return packageList

    def isEnabled(self, view, args):
        return not PackageSelectedForInstallation.download.func.running

################################################################################

class PackageSelectedForInstallation(sublimeplugin.WindowCommand):
    def isEnabled(self, window, args):
        return not self.download.func.running

    def run(self, window, args):
        self.name = args[0]

        self.url = packageRoot() + self.name + ".sublime-package"

        self.localPackageRoot = sublime.packagesPath()
        self.destination = os.path.join (
            sublime.installedPackagesPath(), '%s.sublime-package' % self.name )

        self.window = window

        self.packageFolder = os.path.join(self.localPackageRoot, self.name)

        existsAlready = ""
        if os.path.exists(self.packageFolder):
            existsAlready = ( "\n\n This package is already installed "
                              "and will be upgraded. Backups will be made "
                              "of modified files" )

        unpackAnswer = sublime.questionBox (
            " Do you wish to download package and install in '%s'?%s " % (
                self.packageFolder, existsAlready) )

        if not unpackAnswer:
            return

        self.download()
        self.download_monitor()

    def install(self):
        sublime.messageBox("Unpacked to %s" % self.packageFolder)

        # Open the readme file
        README = join(self.packageFolder, 'README.txt')
        if exists(README):
            self.window.openFile(README)

        notify_of_conflicts_if_any()

    @threaded(finish=install)
    def download(self):
        urllib.urlretrieve(self.url, self.destination)
        self.upgradePackage(self.destination, self.packageFolder)

    @staggered(250)
    def download_monitor(self):
        i=0
        indicators = ['|', '/', '-', '\\']

        while self.download.func.running:
            i+=1
            yield

            sublime.statusMessage (
                "Downloading %s: %s%s" % (
                    self.name, indicators[i%4], ('.'  * (i % 100)) ) )

        sublime.statusMessage('Download Complete')

    def upgradePackage(self, zipPath, destinationFolder):
        old = os.path.join (
            os.path.dirname(sublime.packagesPath()),
            'Pristine Packages', os.path.basename(zipPath) )

        upgradeArchive(zipPath, old, destinationFolder)

################################################################################