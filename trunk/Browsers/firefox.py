import telnetlib, re, time, subprocess, webbrowser

from windows import findAppHandle, SetForegroundWindow

# http://www.koders.com/lisp/fidF13DCDF15FD63D89F363654D9CB840DCF84C81DA.aspx?s=TV+Raman#L2

repl_re = re.compile("(.*?)repl[0-9]{0,2}>", re.DOTALL | re.MULTILINE)
firefox_path = '"H:\PortableApps\FirefoxPortable\FirefoxPortable.exe"'
firefox_window_class = "MozillaUIWindowClass"

def check_mozlab_installed(sublime):
    MozLabURL = "http://repo.hyperstruct.net/mozlab/current/mozlab-current.xpi"
    
    question =("This plugin requires firefox open and MozLab intalled\n"
               "Make sure MozRepl Telnet server is set to 'Activate on "
               "startup'. Tools -> MozRepl\n\n"
                "Do you need to download MozLab ?")
    
    if sublime.questionBox(question):
        try: webbrowser.open(MozLabURL)
        except WindowsError:
            sublime.setClipboard(MozLabURL)
            sublime.messageBox("Tried browsing to MozLab\n"
                               "Url also in clipboard")

class FireFox(object):
    connection = None
    hwnd = None

    def __init__( self, server = 'localhost',  port = 4252, connect=1):
        if connect: 
            self.connect(server, port, 2) or (
                self.start() and self.connect(server, port, 10)
            )

    def start(self, ff_path = None, wait = 5):
        proc = subprocess.Popen(ff_path or firefox_path)
        time.sleep(wait)
        return proc

    def connect(self, server = None, port = None, time_out = 10):
        t = time.time()

        while (time.time() - t) < time_out:
            try:
                self.connection = telnetlib.Telnet(server, port)
                break
            except:
                time.sleep(0.2)

        t = time_out - (time.time() - t)

        if self.connection: self.connection.expect([repl_re], t)
        return self.connection

    def write(self, val, flush = 0):
        self.connection.write('%s;\n' % val)
        if flush: self.read()

    def read(self, as_a = None, time_out = 10):
        expected = self.connection.expect([repl_re], time_out)
        expected = expected[1].group(1).rstrip()
        return as_a(expected) if as_a else expected
    
    def activate(self):
        SetForegroundWindow(self.HWND)

    def eval(self, val):
        self.write(val)
        return self.read(eval)

    def Navigate(self, url):
        if '://' not in url: url = "http://%s" % url
        self.write("content.location.href = %r" % url, 1)

    def Refresh(self):
        self.write("BrowserReloadWithFlags(16)", 1)

    def _get_title(self): return self.eval('title')
    def _set_title(self, title): self.write('title = %r' % title, 1)
    title = property(_get_title, _set_title)

    @property
    def lastUrl(self): return self.eval('gLastValidURLStr')

    @property
    def HWND(self):
        self.hwnd = self.hwnd or findAppHandle(firefox_window_class, self.title)
        return self.hwnd

if __name__ == '__main__':
    firefox = FireFox ()
    print firefox.lastUrl
    print firefox.title
    print firefox.HWND