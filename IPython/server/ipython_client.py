################################################################################

# Std Libs
from __future__ import with_statement

import sys

import Pyro.core

################################################################################

IPython = Pyro.core.getProxyForURI("PYROLOC://localhost:7380/IPython")

print IPython.complete('', line='from os.path import ')

# IPython.push('ls\n')

################################################################################