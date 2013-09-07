# GIANT INDEX
# v0.1

import os
import sys
import contextlib
import ConfigParser
import MySQLdb


class DatabaseConnection(object):
    def __init__(self, host, user, passwd, db):
        self._db = MySQLdb.connect(
            host=host, user=user, passwd=passwd, db=db)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close the database connection."""
        self._db.close()

    def pathIsIndexed(self, path):
        """Return true if the path is in the database, false otherwise."""

        with contextlib.closing(self._db.cursor()) as c:
            c.execute('SELECT id FROM documents WHERE path = %s', (path,))
            return c.fetchone() is not None

    def getDocumentPath(self, docID):
        """Return the path of the document with the given ID."""

        with contextlib.closing(self._db.cursor()) as c:
            c.execute('SELECT path FROM documents WHERE id = %s', (docID,))
            return c.fetchone()[0]

    def addDocument(self, path):
        """
        Create a blank database entry
        for the document at the given path,
        return a document id.
        """

        with contextlib.closing(self._db.cursor()) as c:
            c.execute("""
                    INSERT INTO documents (id, path, modified, duration, width, height, size)
                    VALUES (NULL, %s, CURRENT_TIMESTAMP, NULL, NULL, NULL, 0)""", (path,))
            self._db.commit()

            c.execute('SELECT id FROM documents WHERE path = %s', (path,))
            return c.fetchone()[0]

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

        with contextlib.closing(self._db.cursor()) as c:
            c.execute(
                'UPDATE documents SET modified = %s, duration = %s, width = %s, height = %s, size = %s WHERE id = %s',
                (modified, duration, width, height, size, docID))
            self._db.commit()


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
        print(db.pathIsIndexed('/home/pghjgublic/test.txt'))
        #db.updateAttributes(1)
