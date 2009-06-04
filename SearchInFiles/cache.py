#!/usr/bin/env python
#coding: utf8
#################################### IMPORTS ###################################

# Std Libs
from __future__ import with_statement

import sys
import os
import pprint
import threading
from datetime import datetime

# App Libs
try:                 import sublime
except ImportError:  sublime = None

################################### CONSTANTS ##################################

MAX_AGE = 60 * 60 # seconds

################################################################################

"""

TODO
====

Cache mechanism:
    Invalidate cache if any of:
        File is open in any of the active window views
        File size, date has changed etc

File list interface:
    Mechanism for feeding files

        Project files

        Current directory files

"""

class SearchResultsCache(dict):
    def __init__(self):
        self.lock = threading.RLock()

        if sublime:
            self.clean_up()

    def clean_up(self):
        now = datetime.now()

        with self.lock:
            for key in list(self):
                delta = now - self[key]['cached_at']
    
                if delta.seconds > MAX_AGE:
                    del self[key]

        sublime.setTimeout(self.clean_up, 1000 * 60 * 10)

    def get(self, (f, search), setter=None):
        stat = tuple(os.stat(f))
        results = dict.get(self, (f, search))
        cached = results.get(stat) if results else None
        new_results = None

        if sublime:
            aw = sublime.activeWindow()
            for v in aw.views():
                if v.fileName() == f and v.isDirty():
                    cached = False
                    break

        if not (results or cached):
            new_results = setter()
            self[(f, search)] = { stat       : new_results, 
                                  'cached_at': datetime.now() }

        return cached or new_results

################################################################################