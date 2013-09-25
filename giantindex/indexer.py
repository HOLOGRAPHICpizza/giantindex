import os
import settings
import index
import collections


class FileScanners(object):
    def __init__(self, ndex):
        self.ndex = ndex
        self.ALL_SCANNERS = (self.music, self.image, self.video)

        # initialize tags
        tags = ('extension', 'music', ('duration', True), ('bitrate', True),
                'genre', 'artist', 'album', 'track', 'name', ('width', True),
                ('height', True), 'image', 'video')

        tag_set = set()
        num_tags = {}
        for tag in tags:
            if isinstance(tag, collections.Container):
                tag_set.add(str(tag[0]))
                num_tags[tag] = tag[1] is True
            else:
                tag_set.add(str(tag))
                num_tags[tag] = False

        ndex_tags = self.ndex.get_all_tags()
        unregd = tag_set.difference(ndex_tags)
        for tag in unregd:
            self.ndex.add_tag(tag, num_tags[tag])

    def music(self, f):
        """Detect mp3, flac. Tag them."""
        doc = self.ndex.get_document(f)
        if f.lower().endswith('.mp3') or f.lower().endswith('.flac'):
            # tag da metadata!
            self.ndex.tag_document(doc, 'music')
            if f.lower().endswith('.mp3'):
                self.ndex.tag_document(doc, ('extension', 'mp3'))
            else:
                self.ndex.tag_document(doc, ('extension', 'flac'))

        elif f.lower().endswith('.m4a'):
            # tag with GET OFF M4A
            self.ndex.tag_document(doc, ('extension', 'm4a'))

    def image(self, f):
        """Detect png, jpg, etc. get resolution."""
        flower = f.lower()
        e = None
        if flower.endswith('.png'):
            e = 'png'
        elif flower.endswith('.jpg') or flower.endswith('.jepg'):
            e = 'jpg'
        elif flower.endswith('.xcf'):
            e = 'xcf'
        elif flower.endswith('.svg'):
            e = 'svg'
        elif flower.endswith('.gif'):
            e = 'gif'
        elif flower.endswith('.bmp'):
            e = 'bmp'
        elif flower.endswith('.ico'):
            e = 'ico'

        if e is not None:
            doc = self.ndex.get_document(f)
            self.ndex.tag_document(doc, 'image', ('extension', e))

    def video(self, f):
        """Detect avi, mov, etc. get length, resoultion, etc."""
        flower = f.lower()
        e = None
        if flower.endswith('.avi'):
            e = 'avi'
        elif flower.endswith('.mov'):
            e = 'mov'
        elif flower.endswith('.mkv'):
            e = 'mkv'
        elif flower.endswith('.mpeg') or flower.endswith('.mpg'):
            e = 'mpeg'
        elif flower.endswith('.m4v'):
            e = 'm4v'
        elif flower.endswith('.avc'):
            e = 'avc'

        if e is not None:
            doc = self.ndex.get_document(f)
            self.ndex.tag_document(doc, 'video', ('extension', e))


def index_file(ndex, path, scanners, reload_tags=False):
    """
    Index a file.
    Add any new files to the index and load auto tags.
    For existing files, update modified and size.
    
    index: Index to act on
    path: path of file
    reload_tags: load auto tags on existing files if True

    Throw exception on index error or io error.
    """
    tp = os.path.abspath(path)

    stats = os.stat(tp)
    doc = index.Document(tp, long(stats.st_mtime), long(stats.st_size))

    doc_id, new = ndex.add_document(doc)

    if new:
        print("add %s" % (tp,))
    else:
        print("update %s" % (tp,))

    if new or reload_tags:
        # load the awesome shit
        for func in scanners:
            func(tp)


def index_directory(ndex, path, scanners, exclude=None, reload_tags=False):
    """
    Recursively index a directory.
    Add any new files to the index and load auto tags.
    For existing files, update modified and size.

    index: Index to act on
    path: path of directory to index
    exclude: collection of paths to skip
    reload_tags: load auto tags on existing files?
    
    Throw exception on index error or io error.
    """
    walk_path = os.path.abspath(path)
    print("Indexing %s:" % (walk_path,))

    for directory, subdirs, files in os.walk(walk_path):
        if exclude is None or directory not in exclude:
            for f in files:
                tp = os.path.abspath(os.path.join(directory, f))
                if exclude is None or tp not in exclude:
                    index_file(ndex, tp, scanners, reload_tags)


if __name__ == '__main__':
    cfg = settings.get()
    if cfg is None:
        raise settings.ConfigurationNotFoundException()

    with index.Index(cfg['host'], cfg['user'], cfg['passwd'], cfg['db']) as ndx:
        scanners = FileScanners(ndx).ALL_SCANNERS

        ncludes = set()
        for path in cfg['include'].split('|'):
            ncludes.add(os.path.abspath(path))

        xclude = cfg.get('exclude', None)
        xcludes = set()
        if xclude is not None:
            for path in xclude.split('|'):
                xcludes.add(os.path.abspath(path))

        for path in ncludes:
            index_directory(ndx, path, scanners, exclude=xcludes)
