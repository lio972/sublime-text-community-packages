################################################################################

import threading, Queue, sys

# for markdown2
sys.argv = []
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
    def __init__(self, OQ, num_workers = 8, queue_size = 8):
        self.OQ = OQ
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
        self.queue.put_nowait( partial(f, *args, **kwargs) )

    def stop(self):
        self.queue.put(STOP)

    def threadloop(self):
        while True:
            arg = self.queue.get()
            if arg is STOP:
                self.queue.put(STOP)
                self.queue.task_done()
                break
            else:
                try:
                    self.OQ.put(("BUFFER", arg()))
                finally:
                    self.queue.task_done()

    def wait(self):
        self.queue.join()

################################################################################