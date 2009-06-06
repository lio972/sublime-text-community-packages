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

    def get(self, (f, search), setter=None):
        stat = tuple(os.stat(f))
        results = dict.get(self, (f, search))
        cached = results.get(stat) if results else None
        new_results = None

        if not cached:
            new_results = setter()
            self[(f, search)] = { stat       : new_results, 
                                  'cached_at': datetime.now() }
        
        return cached or new_results

################################################################################