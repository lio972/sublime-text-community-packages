import sublime, sublimeplugin
import os, os.path, sys, stat
import cPickle as pickle
from datetime import datetime
from pprint import pprint as pp

class QuickMRUCommand(sublimeplugin.WindowCommand):
	"""
	Shows a quick panel with the most recently closed files and the	files closed most often.
	"""

	dbfilename = sublime.packagesPath() + "/QuickMRU/QuickMRU.db" # is there a better way to get the plugin's folder?

	__db = None

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
			myfile = open(self.dbfilename, "r")
			self.__db = pickle.load(myfile)
			myfile.close()
		except IOError:
			print "QuickMRU: DB not found, creating new one"
			self.__db = {}

	def dumpDB(self):
		# print "QuickMRU: dumping DB to disk"
		myfile = open(self.dbfilename, "w")
		pickle.dump(self.db, myfile)
		myfile.close()

	def trimDB(self):
		print "QuickMRU: Trimming DB"
		db = self.db
		latest       = sorted(db.keys(), key=lambda x:db[x]['date'   ], reverse=True)
		mostFrequent = sorted(db.keys(), key=lambda x:db[x]['counter'], reverse=True)
		files = set(mostFrequent[:100] + latest[:100])
		newDB = {}
		for x in files:
			newDB[x]=db[x]
		del newDB[None]

		self.db = newDB


	def onClose(self, view):
		if not view.fileName():
			return

		now = datetime.utcnow()
		if(view.fileName() in self.db):
			self.db[view.fileName()]['counter'] += 1
			self.db[view.fileName()]['date'] = now
		else:
			self.db[view.fileName()] = {'counter': 1, 'date': now}

		self.dumpDB()

		# if the DB exceeds 128kb, trim it
		file_stats = os.stat(self.dbfilename)
		file_size = file_stats[stat.ST_SIZE]
		if file_size >= 128 * 1024**2:
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

		latest       = sorted(db.keys(), key=lambda x:db[x]['date'   ], reverse=True)
		mostFrequent = sorted(db.keys(), key=lambda x:db[x]['counter'], reverse=True)
		files = sorted(
			set(mostFrequent[:10] + latest[:10]),
			key=lambda x:db[x]['date'],
			reverse=True)

		# remove unavailable files (i.e. deleted, on a removable drive, etc)
		files = [f for f in files if f and os.path.isfile(f)]

		display = [self.getDesc(f) for f in files]
		# pp(files)
		# print len(db.keys())
		window.showQuickPanel("", "open", files, display, sublime.QUICK_PANEL_FILES)
