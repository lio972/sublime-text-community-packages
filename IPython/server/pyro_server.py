################################################################################

# Std Libs
import threading

import IPython
ip = IPython.ipapi.get()
IP= ip.IP

# 3rd Party Libs
import Pyro.core

class IPython(Pyro.core.ObjBase):
    def complete(self, fragment, line):
        completion = IP.Completer.complete(fragment, 0, line_buffer=line)
        matches    = IP.Completer.matches 

        return completion, matches
    
    def push(self, lines):
        return ip.runlines(lines)

    def input_hist(self):
        return list(IP.input_hist)

################################################################################    

def __ss():
    Pyro.core.initServer()
    daemon=Pyro.core.Daemon(port=7380, norange=1)
    uri=daemon.connect(IPython(), "IPython")
    
    print "The daemon runs on port:",daemon.port
    print "The object's uri is:",uri
    
    server_thread = threading.Thread(target=daemon.requestLoop)
    server_thread.setName('IPython')
    server_thread.setDaemon(True)
    server_thread.start()

# if 1: start_server()