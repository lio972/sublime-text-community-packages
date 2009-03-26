################################################################################

import threading, Queue, sys, os, unittest

# for markdown2
if __name__ != '__main__':
    sys.argv = []
else:
    sys.path.append (
        os.path.join(os.path.dirname(sys.argv[0]), 'lib')
    )

import markdown2, smartypants, textile

from functools import partial

################################################################################

def CONSTANTS(num):
    for x in xrange(num): yield object()

################################################################################

markups={}

def proc_markdown(a):
    return smartypants.smartyPants(markdown2.markdown(a))

def proc_textile(a):
    return smartypants.smartyPants(textile.textile(str(a)))

markups["Packages/Markdown/Markdown.tmLanguage"] = proc_markdown
markups['Packages/Textile/Textile.tmLanguage'] = proc_textile

################################################################################

DEBUG = 0

STOP = object()

class WorkerQueue(object):
    def __init__(self, ie, num_workers = 8, queue_size = 8):
        self.ie = ie
        self.queue = Queue.Queue(queue_size)
        self.pool = []
        self._setup_workers(num_workers)

    def _setup_workers(self, num_workers):
        self.pool = []

        for _ in range(num_workers):
            self.pool.append(threading.Thread(target=self.threadloop))

        for a_thread in self.pool:
            a_thread.setDaemon(True)
            a_thread.start()

    def put(self, f, *args, **kwargs):
        try: self.queue.put_nowait( partial(f, *args, **kwargs) )
        except Queue.Full: pass

    def stop(self):
        self.queue.put(STOP)
        for thread in self.pool:
            thread.join()

    def threadloop(self):
        while True:
            arg = self.queue.get()
            if arg is STOP:
                self.queue.put(STOP)
                self.queue.task_done()
                break
            else:
                try:
                    self.ie.buffer(arg())
                finally:
                    self.queue.task_done()

    def wait(self):
        self.queue.join()

################################################################################

class WorkerQueueTest(unittest.TestCase):
    def test_stop(self):
        ie = lambda x: x
        ie.buffer = lambda x:x
        
        wq = WorkerQueue(ie)
        
        self.assert_(len(wq.pool) > 0)
        for t in wq.pool: self.assert_(t.isAlive())

        for i in xrange(200): wq.put(lambda x: x+1, i)

        wq.stop()
        for t in wq.pool: self.assert_(not t.isAlive())

        self.assert_(wq.queue.get() is STOP)

if __name__ == '__main__':
   unittest.main()