################################################################################

import time

def time_function(times=1):
    def decorator(f):
        def wrapper(*args, **kw):
            total_time = 0
            for t in xrange(times):
                t = time.time()
                result = f(*args, **kw)
                total_time += time.time() - t
            print f.__name__, total_time / times
            return result
        return wrapper
    return decorator

################################################################################