import sys
import os
import ConfigParser

def index_file(index, path, reload_tags=False):
    """
    Index a file.
    Add any new files to the index and load auto tags.
    For existing files, update modified and size.
    
    index: Index to act on
    path: path of file
    reload_tags: load auto tags on existing files if True

    Throw exception on index error or io error.
    """
    pass


def index_directory(index, path, excludePaths=(), reload_tags=False):
    """
    Recursively index a directory.
    Add any new files to the index and load auto tags.
    For existing files, update modified and size.

    index: Index to act on
    path: path of directory to index
    excludePaths: collection of paths to skip
    reload_tags: load auto tags on existing files?
    
    Throw exception on index error or io error.
    """

    for directory, subdirs, files in os.walk(root):
        for f in files:
            if not db.pathIsIndexed(f):
                doc = db.addDocument(f)
                db.updateAttributes(doc)
                print(os.path.join(directory, f))

def get_settings():
    """
    Return a dict of settings and their values
    from loading a settings file.
    Throw exception if not found.
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


#TODO: Migrate.
    def update_attributes(self, path):
        """
        Update the indexed attributes for the given path.

        Throw exception if path is not indexed.
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

if __name__ == '__main__':

    cfg = getSettings()

    with DatabaseConnection(cfg['host'], cfg['user'], cfg['passwd'], cfg['db']) as db:
        print(db.pathIsIndexed('/home/pghjgublic/test.txt'))
        #db.updateAttributes(1)
