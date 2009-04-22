import sublime, sublimeplugin
import os, os.path, sys, stat
import cPickle as pickle
import datetime
from pprint import pprint as pp

class QuickMRUCommand(sublimeplugin.WindowCommand):
	"""
	Shows a quick panel with the most recently closed files and the	files closed most often.
	"""
	
	filename = sublime.packagesPath() + "/QuickMRU/QuickMRU.db" # is there a better way to get the plugin's folder?
	
	def getDB(self):
		try:
			myfile = open(self.filename, "r")
			db = pickle.load(myfile)
			myfile.close()
		except IOError:
			db = {}
		return db
	
	def trimDB(self):
		db = self.getDB()
		latest       = sorted(db.keys(), key=lambda x:db[x]['date'   ], reverse=True)
		mostFrequent = sorted(db.keys(), key=lambda x:db[x]['counter'], reverse=True)
		files = set(mostFrequent[:100] + latest[:100])
		newDB = {}			
		for x in files:
			newDB[x]=db[x]
		
		myfile = open(self.filename, "w")
		pickle.dump(newDB, myfile)
		myfile.close()
		
	def onClose(self, view):
		db = self.getDB();

		now = datetime.datetime.today();
		if(view.fileName() in db):
			db[view.fileName()]['counter'] += 1
			db[view.fileName()]['date'] = now
		else:
			db[view.fileName()] = {'counter': 1, 'date': now}
			
		myfile = open(self.filename, "w")
		pickle.dump(db, myfile)
		myfile.close()
		
		# if the DB exceeds 128kb, trim it
		file_stats = os.stat(self.filename)
		file_size = file_stats[stat.ST_SIZE];
		if file_size >= 128 * 1024**2:
			self.trimDB()
			
	def getDescription(self, item, counter, date):		
		delta = datetime.datetime.today() - date
		days = delta.days
		minutes = delta.seconds / 60
		hours = minutes / 60
		if days == 0 and hours == 0:
			age = "%2d mins " % (minutes,)
		elif days == 0:		
			age = "%2d hours" % (hours,)
		else:
			age = "%2d days " % (days,)
		
		return "%2dx, %s - %s" % (counter, age, item)
		
	def run(self, window, args):
		db = self.getDB();
			
		latest       = sorted(db.keys(), key=lambda x:db[x]['date'   ], reverse=True)
		mostFrequent = sorted(db.keys(), key=lambda x:db[x]['counter'], reverse=True)
		files = sorted(
			set(mostFrequent[:10] + latest[:10]),
			key=lambda x:db[x]['date'],
			reverse=True)
		
		display = map(lambda x: self.getDescription(x, db[x]['counter'], db[x]['date']), files)

		window.showQuickPanel("", "open", files, display, sublime.QUICK_PANEL_FILES)