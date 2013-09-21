import os
import settings
import index


def file_scanners():
    ret = []

    def s_music(f):
        """Detect mp3, flac. Tag them."""
        if f.lower().endswith('.mp3') or f.lower().endswith('.flac'):
            # tag da metadata!
            pass

        elif f.lower().endswith('.m4a'):
            # tag with GET OFF M4A
            pass
    ret.append(s_music)

    def s_image(f):
        """Detect png, jpg, etc. get resolution."""
        pass
    ret.append(s_image)

    def s_video(f):
        """Detect avi, mov, etc. get length, resoultion, etc."""
        pass
    ret.append(s_video)

    return ret


def index_file(ndx, path, reload_tags=False):
    """
    Index a file.
    Add any new files to the index and load auto tags.
    For existing files, update modified and size.
    
    index: Index to act on
    path: path of file
    reload_tags: load auto tags on existing files if True

    Throw exception on index error or io error.
    """
    stats = os.stat(path)
    doc = index.Document(path, long(stats.st_mtime), long(stats.st_size))

    doc_id, new = ndx.add_document(doc)

    if new or reload_tags:
        # load the awesome shit
        for func in file_scanners():
            func(path)


def index_directory(ndx, path, exclude=None, reload_tags=False):
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

    for directory, subdirs, files in os.walk(path):
        for f in files:
            tp = os.path.join(directory, f)
            if exclude is not None and tp not in exclude:
                print(tp)
                index_file(ndx, tp, reload_tags)


if __name__ == '__main__':

    cfg = settings.get()
    if cfg is None:
        raise settings.ConfigurationNotFoundException()

    with index.Index(cfg['host'], cfg['user'], cfg['passwd'], cfg['db']) as ndx:
        nclude = cfg['include'].split('|')

        xclude = cfg.get('exclude', None)
        if xclude is not None:
            xclude = xclude.split('|')

        for path in nclude:
            index_directory(ndx, path, exclude=xclude)
