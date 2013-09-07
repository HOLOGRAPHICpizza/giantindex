# GIANT INDEX
# v0.1

import os
import sys
import MySQLdb
import ConfigParser

class DatabaseConnection:
	def __init__(self, host, user, passwd, db):
		self._db = MySQLdb.connect(
				host=host, user=user, passwd=passwd, db=db)
		#TODO: The connection should be closed.

	def pathIsIndexed(self, path):
		"""Return true if the path is in the database, false otherwise."""
		c = self._db.cursor()
		
		c.execute('SELECT id FROM documents WHERE path = %s', (path,))

		ret = c.fetchone() != None

		c.close()
		return ret

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

	def updateAttributes(self, documentID):
		"""
		Updates all attributes of and adds any applicable tags
		to the document with the given ID.
		"""
		pass

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
	Return the multiple string values of: hostname, username, password, database
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

	host = config.get('database', 'host')
	user = config.get('database', 'user')
	passwd = config.get('database', 'passwd')
	dbName = config.get('database', 'db')

	return host, user, passwd, dbName

if __name__ == '__main__':

	host, user, passwd, dbName = getSettings()
	
	db = DatabaseConnection(host, user, passwd, dbName)
	
	print(db.addDocument('XXXXXXXXXXXXX'))


