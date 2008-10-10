if __name__ == '__main__':
    import xmlrpclib
    import sys
    sublime = xmlrpclib.Server('http://localhost:8000')
    print sublime.testServer()