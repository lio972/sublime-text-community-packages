from __future__ import with_statement

import os, sys, stat
from os import path
import cPickle as pickle
from datetime import datetime
# from pprint import pprint as pp
import functools

import sublime, sublimeplugin


# Taken from Sublimator's AAALoadFirstExtensions
def onIdle(ms=1000):
	def decorator(func):
		func.pending = 0
		@functools.wraps(func)
		def wrapped(*args, **kwargs):
			def idle():
				func.pending -= 1
				if func.pending is 0:
					func(*args, **kwargs)
			func.pending +=1
			sublime.setTimeout(idle, ms)
		return wrapped
	return decorator
    
class QuickMRUCommand(sublimeplugin.WindowCommand):
	"""
	Shows a quick panel with the most recently closed files and the	files closed most often.
	"""

	def __init__(self):
		sublimeplugin.WindowCommand.__init__(self)
		self.__db = None
		# pluginDir = path.dirname(path.realpath(__file__))
		# self.dbfilename = path.join(pluginDir, "QuickMRU.db")
		self.dbfilename = sublime.packagesPath() + "/QuickMRU/QuickMRU.db" # is there a better way to get the plugin's folder?

	def _get_db(self):
		if(self.__db is None): self.reloadDB()
		return self.__db

	def _set_db(self, value):
		self.__db = value
		self.dumpDB()

	db = property(_get_db, _set_db)

	def reloadDB(self):
		# print "QuickMRU: loading DB from disk"
		try:
			with open(self.dbfilename, "r") as myfile:
				self.__db = pickle.load(myfile)
		except IOError:
			print "QuickMRU: DB not found, creating new one"
			self.__db = {}

	@onIdle(500)
	def dumpDB(self):
		# print "QuickMRU: dumping DB to disk"
		with open(self.dbfilename, "w") as myfile:
			pickle.dump(self.db, myfile)

	@onIdle(500)
	def trimDB(self):
		print "QuickMRU: Trimming DB"
		db = self.db
		latest       = sorted(db, key=lambda x:db[x]['date'   ], reverse=True)
		mostFrequent = sorted(db, key=lambda x:db[x]['counter'], reverse=True)
		files = set(mostFrequent[:200] + latest[:200])
		newDB = {}
		for x in files:
			newDB[x] = db[x]

		self.db = newDB


	def onClose(self, view):
		if not view.fileName():
			return
		
		if view.fileName().find('\\sublimescp_') != -1:
			# skip WinSCP temporary files
			return

		now = datetime.utcnow()
		if(view.fileName() in self.db):
			self.db[view.fileName()]['counter'] += 1
			self.db[view.fileName()]['date'] = now
		else:
			self.db[view.fileName()] = {'counter': 1, 'date': now}

		self.dumpDB()

		# if the DB is becoming too large, trim it
		file_stats = os.stat(self.dbfilename)
		file_size = file_stats[stat.ST_SIZE]
		if file_size >= 256 * 1024:
			self.trimDB()

	def getDesc(self, item):
		counter = self.db[item]['counter']
		date    = self.db[item]['date']

		delta = datetime.utcnow() - date
		days = delta.days
		minutes = delta.seconds / 60
		hours = minutes / 60

		if days == 0 and hours == 0:
			age = "%2d mins " % minutes
		elif days == 0:
			age = "%2d hours" % hours
		else:
			age = "%2d days " % days

		return "%2dx, %s - %s" % (counter, age, item)

	def run(self, window, args):
		db = self.db

		latest       = sorted(db, key=lambda x:db[x]['date'   ], reverse=True)
		mostFrequent = sorted(db, key=lambda x:db[x]['counter'], reverse=True)
		files = sorted(
			set(mostFrequent[:20] + latest[:20]),
			key=lambda x:db[x]['date'],
			reverse=True)

		# hide unavailable files (i.e. deleted, on a removable drive, etc)
		files = [f for f in files if f and path.isfile(f)]

		display = [self.getDesc(f) for f in files]
		# pp(files)
		# print len(db.keys())
		window.showQuickPanel("", "open", files, display, sublime.QUICK_PANEL_FILES | sublime.SELECT_PANEL_MONOSPACE_FONT)