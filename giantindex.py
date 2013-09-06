# GIANT INDEX
# v0.1

import os
import sys

def pathIsIndexed(path):
	"""Return true if the path is in the database, false otherwise."""
	return True

def addDocument(path):
	"""
	Create a blank database entry
	for the document at the given path,
	return a document id.
	"""
	return -1

def updateAttributes(documentID):
	"""
	Updates all attributes of and adds any applicable tags
	to the document with the given ID.
	"""
	pass

def scanNewFiles(root):
	"""
	Walk the given directory and
	add any files to the database that are not already in it.
	
	Also loads up attributes, tags, and everything!
	"""
	
	print('Scanning for new files...')
	for directory, subdirs, files in os.walk(root):
		for f in files:
			if not pathIsIndexed(f):
				doc = addDocument(f)
				updateAttributes(doc)
				print(os.path.join(directory, f))

if __name__ == '__main__':
	root = os.getcwd()
	
	if len(sys.argv) > 1:
		root = sys.argv[1]
	
	if not os.access(root, os.R_OK):
		print('Can not read the directory %s!', root)
		sys.exit(1)
	
	scanNewFiles(root)

