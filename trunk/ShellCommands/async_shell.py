#!/usr/bin/env python
#coding: utf8
#################################### IMPORTS ###################################

# Std Libs
import functools
import sys
import os
import pprint
import subprocess

from uuid import uuid4 as random_hash

# App Libs
import sublime
import sublimeplugin

import async

TIMEOUT = 1

if 1:
    CMD_TYPE = 'cmd'
    TAIL = '\r\n'
else:
    CMD_TYPE = 'bash'
    TAIL = '\n'

################################################################################

def ensure_shell(f):
    @functools.wraps(f)
    def check(self, view, args):
        if not self.shell:
            self.shell = async.Popen( CMD_TYPE, 
                                      stdin  = async.PIPE, 
                                      stdout = async.PIPE,
                                      stderr = subprocess.STDOUT,
                                      shell  = 1 )

            expected_cmd(self.shell, 'set')

        return f(self, view, args, self.shell)

    return check

def expected_cmd(shell, cmd, timeout=TIMEOUT, tail=TAIL):
    expect = str(random_hash())

    shell.send_all(cmd  + tail)
    
    flushed_cmd_line = shell.recv()
    # print shell.stderr.readline()
    
    shell.send_all('echo %s%s' % (expect, tail))

    lines = [None]
    t, wait, waited = 1.5, 0, 0

    while waited < timeout:
        wait = min(t / 1000, 0.1)
        waited += wait

        lines.extend (
            shell.read_async(e=0, wait=wait).splitlines(0)
        )

        try:
            t == t ** 2
        except OverflowError:
            t = float(int(t) ** 2)

        if expect in lines:
            lines = lines[:lines.index(expect)]
            break

    return flushed_cmd_line, lines[1:]

################################# AUTOCOMPLETE #################################

# def auto_complete(view, pos, prefix, completions):
#     if not completions:
#         candidates = []

#         view.findAll('([a-zA-Z_]+)', 0, '$1', candidates)
    
#         for m in set(c for c in candidates if c.lower().startswith(prefix)):
#             completions.append(m)
    
#     return completions

# from AutoComplete import AutoCompleteCommand
# AutoCompleteCommand.completionCallbacks['bash'] = auto_complete                                                                        
    
################################################################################


class AsyncCommand(sublimeplugin.TextCommand):
    shell = None

    @ensure_shell
    def run(self, view, args, shell):
        reg = view.fullLine(view.sel()[0])
        cmd = view.substr(reg).encode('utf8').strip()

        if cmd:
            flushed, lines = expected_cmd(shell, cmd)
            
            print flushed

            if CMD_TYPE == 'cmd' and lines:
                lines[-1] = lines[-1][:-41]

            view.runCommand('moveTo eol')
            view.runCommand('insertAndDecodeCharacters', ['\n\n'])

            lines = '\n'.join(lines[1:]).decode('utf8')

            view.runCommand('insertInlineSnippet', ['$PARAM1$0', lines])
            view.runCommand('insertAndDecodeCharacters', ['\n'])

################################################################################