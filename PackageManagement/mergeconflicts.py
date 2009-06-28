#!/usr/bin/env python
#coding: utf8
#################################### IMPORTS ###################################

# Std Libs

from os.path import join, pardir, dirname, exists, splitext, split

import sublime
import sublimeplugin

from pluginhelpers import staggered
from PackageSetup import upgradeLog, backupName

################################################################################

conflicts = upgradeLog['conflicts']

################################################################################

def notify():
    if conflicts:
        conflicts_log = '\n'.join(conflicts)
        sublime.messageBox(
            'You have Package update conflicts:\n\n\n%s' % conflicts_log
        )
        sublime.setClipboard(conflicts_log)

notify()

class MergePackageUpgradeConflicts(sublimeplugin.TextCommand):
    def isEnabled(self, view, args):
        return conflicts

    @staggered(0)
    def run(self, view, args):
        f = conflicts.pop()

        yield sublime.runCommand('newWindow')
        yield 5 # wait 5 milliseconds to resume command

        window = sublime.activeWindow()

        yield window.runCommand('layoutTripleVert')

        files  = [backupName(f, 'bak')]
        if exists(f): files.insert(0, f)
        parent = backupName(f, 'parent')

        if exists(parent):
            files.insert(1, parent)

        for i, f in enumerate(files):
            yield window.openFile(f)
            yield window.runCommand('moveToGroup %s' % i)

        yield 25

        sublime.messageBox({

            1:  'Orphan File ( File deleted in package )',
            2:  'Overwrite',
            3:  '3 way merge'

        }[len(files)])

        yield 50

        sublime.statusMessage (
             '%s more conflicts to merge' % len(upgradeLog['conflicts']) )

################################################################################