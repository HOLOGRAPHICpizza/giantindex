# GIANT INDEX
# v0.1

import os
import sys
import time
import MySQLdb
import ConfigParser

class DatabaseConnection:
	def __init__(self, host, user, passwd, db):
		self._db = MySQLdb.connect(
				host=host, user=user, passwd=passwd, db=db)
		#TODO: The connection should be closed.
	
	def __enter__(self):
		return self

	def __exit__(self):
		self._db.close()
		#TODO: see if that function exists
	
	#TODO: consider 'with' syntax for cursor
	def pathIsIndexed(self, path):
		"""Return true if the path is in the database, false otherwise."""
		c = self._db.cursor()
		
		c.execute('SELECT id FROM documents WHERE path = %s', (path,))

		ret = c.fetchone() != None

		c.close()
		return ret

	def getDocumentPath(self, docID):
		"""Return the path of the document with the given ID."""
		c = self._db.cursor()

		c.execute('SELECT path FROM documents WHERE id = %s', (docID,))
		path = c.fetchone()[0]

		c.close()
		return path

	def addDocument(self, path):
		"""
		Create a blank database entry
		for the document at the given path,
		return a document id.
		"""
		c = self._db.cursor()

		c.execute('INSERT INTO documents (id, path, modified, duration, width, height, size) VALUES (NULL, %s, CURRENT_TIMESTAMP, NULL, NULL, NULL, 0)', (path,))
		self._db.commit()
		
		c.execute('SELECT id FROM documents WHERE path = %s', (path,))
		docID = c.fetchone()[0]

		c.close()
		return docID

	def updateAttributes(self, docID):
		"""
		Updates all attributes of and adds any applicable tags
		to the document with the given ID.
		"""
		path = self.getDocumentPath(docID)
		pathStat = os.stat(path)
		
		#TODO: skip checks if not modified since last scan
		# Modified
		modified = pathStat.st_mtime
		#TODO: is this number in MySQL TIMESTAMP friendly format?

		# Size (in bytes)
		size = pathStat.st_size
		
		# Add Applicable Tags

		
		#TODO: Perhaps retain some info on file type to avoid checking tags

		# Duration
		duration = None
		if hasTag(docID, 'audio') or hasTag(docID, 'video'):
			duration = None #get that duration!

		width, height = None
		if hasTag(docID, 'image') or hasTag(docID, 'video'):
			
			# Width
			width = None #get that width!
			
			# Height
			height = None #get height

		c = self._db.cursor()

		c.execute('UPDATE documents SET modified = %s, duration = %s, width = %s, height = %s, size = %s WHERE id = %s', (modified, duration, width, height, size, docID))
		self._db.commit()
		
		c.close()

def scanNewFiles(root, db):
	"""
	Walk the given directory and
	add any files to the database that are not already in it.
	
	Also loads up attributes, tags, and everything!
	"""
	
	for directory, subdirs, files in os.walk(root):
		for f in files:
			if not db.pathIsIndexed(f):
				doc = db.addDocument(f)
				db.updateAttributes(doc)
				print(os.path.join(directory, f))

def getSettings():
	"""
	Return a dict of settings and their values
	from loading a settings file,
	or exit the program if none is found.
	"""
	#TODO: Prompt the user? Cmd-line args?

	# Locate configuration file
	cfgFile = None
	cfg_name = 'giantindex.cfg'
	if os.access(cfg_name, os.R_OK):
		cfgFile = cfg_name
	elif os.access(os.path.expanduser('~/.' + cfg_name), os.R_OK):
		cfgFile = os.path.expanduser('~/.' + cfg_name)
	elif os.access(os.path.join('/etc/', cfg_name), os.R_OK):
		cfgFile = os.path.join('/etc/', cfg_name)
	else:
		print('Could not load ./giantindex.cfg, ~/.giantindex.cfg, or /etc/giantindex.cfg')
		sys.exit(1)
	
	config = ConfigParser.RawConfigParser()
	config.read(cfgFile)
	
	settings = {}

	for key in ('host', 'user', 'passwd', 'db'):
		settings[key] = config.get('database', key)
	for key in ('include', 'exclude'):
		settings[key] = config.get('indexer', key)
	
	return settings

if __name__ == '__main__':
	
	cfg = getSettings()
	
	with DatabaseConnection(cfg['host'], cfg['user'], cfg['passwd'], cfg['db']) as db:
		db.updateAttributes(1)
		print(db.pathIsIndexed('ds'))


