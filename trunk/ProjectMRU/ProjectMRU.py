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
    
class ProjectMRUCommand(sublimeplugin.WindowCommand):
	"""
	Shows a quick panel with the most recently closed files and the	files closed most often.
	"""

	def __init__(self):
		sublimeplugin.WindowCommand.__init__(self)
		self.__db = None
		# pluginDir = path.dirname(path.realpath(__file__))
		# self.dbfilename = path.join(pluginDir, "ProjectMRU.db")
		self.dbfilename = sublime.packagesPath() + "/ProjectMRU/ProjectMRU.db" # is there a better way to get the plugin's folder?

	def _get_db(self):
		if(self.__db is None): self.reloadDB()
		return self.__db

	def _set_db(self, value):
		self.__db = value
		self.dumpDB()

	db = property(_get_db, _set_db)

	def reloadDB(self):
		# print "ProjectMRU: loading DB from disk"
		try:
			with open(self.dbfilename, "r") as myfile:
				self.__db = pickle.load(myfile)
		except IOError:
			print "ProjectMRU: DB not found, creating new one"
			self.__db = {}

	@onIdle(500)
	def dumpDB(self):
		# print "ProjectMRU: dumping DB to disk"
		with open(self.dbfilename, "w") as myfile:
			pickle.dump(self.db, myfile)
		
		# if the DB is becoming too large, trim it
		file_stats = os.stat(self.dbfilename)
		file_size = file_stats[stat.ST_SIZE]
		if file_size >= 64 * 1024:
			self.trimDB()

	@onIdle(500)
	def trimDB(self):
		print "ProjectMRU: Trimming DB"
		db = self.db
		latest       = sorted(db, key=lambda x:db[x]['date'   ], reverse=True)
		mostFrequent = sorted(db, key=lambda x:db[x]['counter'], reverse=True)
		files = set(mostFrequent[:50] + latest[:50])
		newDB = {}
		for x in files:
			newDB[x] = db[x]

		self.db = newDB


	def onProjectClose(self, window):
		filename = window.project().fileName()
		if not filename:
			return

		now = datetime.utcnow()
		if(filename in self.db):
			self.db[filename]['counter'] += 1
			self.db[filename]['date'] = now
		else:
			self.db[filename] = {'counter': 1, 'date': now}

		self.dumpDB()

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
			set(mostFrequent[:10] + latest[:10]),
			key=lambda x:db[x]['date'],
			reverse=True)

		# hide unavailable files (i.e. deleted, on a removable drive, etc)
		files = [f for f in files if f and path.isfile(f)]

		display = [self.getDesc(f) for f in files]
		# pp(files)
		# print len(db.keys())
		window.showQuickPanel("", "openProject", files, display, sublime.QUICK_PANEL_FILES | sublime.SELECT_PANEL_MONOSPACE_FONT)