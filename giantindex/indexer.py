import os
import settings
import index


def file_scanners(ndx):
    ret = []

    tag_set = set()
    num_tags = {}
    def r_tags(*tags):
        for tag in tags:
            if len(tag) > 1:
                tag_set.add(str(tag[0]))
                num_tags[tag] = tag[1] is True
            else:
                tag_set.add(str(tag))
                num_tags[tag] = False
    def add_tags():
        ndx_tags = ndx.get_all_tags()
        unregd = tag_set.difference(ndx_tags)
        for tag in unregd:
            ndx.add_tag(tag, num_tags[tag])
    r_tags('extension', 'music', ('duration', True), ('bitrate', True),
           'genre', 'artist', 'album', 'track', 'name', ('width', True),
           ('height', True), 'image', 'video')
    add_tags()

    def s_music(f):
        """Detect mp3, flac. Tag them."""
        doc = ndx.get_document(f)
        if f.lower().endswith('.mp3') or f.lower().endswith('.flac'):
            # tag da metadata!
            ndx.tag_document(doc, 'music')
            if f.lower().endswith('.mp3'):
                ndx.tag_document(doc, ('extension', 'mp3'))
            else:
                ndx.tag_document(doc, ('extension', 'flac'))

        elif f.lower().endswith('.m4a'):
            # tag with GET OFF M4A
            ndx.tag_document(doc, ('extension', 'm4a'))
    ret.append(s_music)

    def s_image(f):
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
            doc = ndx.get_document(f)
            ndx.tag_document(doc, 'image', ('extension', e))
    ret.append(s_image)

    def s_video(f):
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
            doc = ndx.get_document(f)
            ndx.tag_document(doc, 'video', ('extension', e))
    ret.append(s_video)

    return ret


def index_file(ndx, path, scanners, reload_tags=False):
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
        for func in scanners:
            func(path)


def index_directory(ndx, path, scanners, exclude=None, reload_tags=False):
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
                index_file(ndx, tp, scanners, reload_tags)


if __name__ == '__main__':

    cfg = settings.get()
    if cfg is None:
        raise settings.ConfigurationNotFoundException()

    with index.Index(cfg['host'], cfg['user'], cfg['passwd'], cfg['db']) as ndx:
        scanners = file_scanners(ndx)

        nclude = cfg['include'].split('|')

        xclude = cfg.get('exclude', None)
        if xclude is not None:
            xclude = xclude.split('|')

        for path in nclude:
            index_directory(ndx, path, scanners, exclude=xclude)
