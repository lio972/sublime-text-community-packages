################################################################################

import time

def time_function(f):
    def wrapper(*args, **kw):
        t = time.time()

        result = f(*args, **kw)
        
        t = time.time() -t

        print args[0].__class__.__name__, f.__name__, t
        
        return result
    return wrapper

################################################################################







