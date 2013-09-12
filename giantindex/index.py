import contextlib
import MySQLdb


class Document(object):
    """Immutable document descriptor."""

    def __init__(self, path, modified, size, doc_id=None, added=None):
        if doc_id is not None:
            self.doc_id = int(doc_id)
        else:
            self.doc_id = None

        if added is not None:
            self.added = long(added)
        else:
            self.added = None

        self.path = str(path)
        self.modified = long(modified)
        self.size = long(size)

class IndexPathConflictException(Exception):
    def __init__(self, path, doc_id):
        self.path = path
        self.doc_id = doc_id

    def __str__(self):
        return "'%s' is already indexed under ID %i." % (self.path, self.doc_id)

class Index(object):
    def __init__(self, host, user, passwd, db):
        self.db = MySQLdb.connect(
            host=host, user=user, passwd=passwd, db=db)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close the database connection."""
        self.db.close()

    def contains_doc_id(self, doc_id):
        """Returns True if a document has this ID, False otherwise."""
        with contextlib.closing(self.db.cursor()) as c:
            c.execute('SELECT id FROM documents WHERE id = %s', (doc_id,))
            return c.fetchone() is not None

    def doc_id_of_path(self, path):
        """Returns the ID of the document with this path if one exists, or None otherwise."""
        with contextlib.closing(self.db.cursor()) as c:
            c.execute('SELECT id FROM documents WHERE path = %s', (path,))
            row = c.fetchone()
            if row is not None:
                return row[0]
            else:
                return None

    def add_document(self, document):
        """
        Add or overwrite the given document in the index.
        document: Document object

        Return the updated document.

        Raises IndexPathConflictException if document.path is non-unique in the index.
        """
        with contextlib.closing(self.db.cursor()) as c:

            path_doc_id = self.doc_id_of_path(document.path)

            # Is an on-file doc_id is specified?
            if document.doc_id is not None and self.contains_doc_id(document.doc_id):
                # Update Document

                # check for path conflicts
                # must be no docs with path or only this doc
                if path_doc_id is None or path_doc_id == document.doc_id:
                    # update db
                    c.execute('UPDATE documents SET path = %s, modified = FROM_UNIXTIME(%s), size = %s WHERE id = %s',
                            (document.path, document.modified, document.size, document.docID))
                else:
                    raise IndexPathConflictException(document.path, path_doc_id)

            else:
                # Insert Document

                # check for path conflicts
                if path_doc_id is not None:
                    raise IndexPathConflictException(document.path, path_doc_id)

                # insert to db new with generated id
                c.execute("""
                        INSERT INTO documents (id, path, added, modified, size)
                        VALUES (DEFAULT, %s, DEFAULT, %s, %s)""",
                        (document.path, document.modified, document.size))
        self.db.commit()

        with contextlib.closing(self.db.cursor()) as c:
            # select new document object
            c.execute('SELECT id, added FROM documents WHERE path = %s', (document.path,))
            row = c.fetchone()
            return Document(
                    document.path,
                    document.modified,
                    document.size,
                    row[0],
                    row[1])
    
    def remove_document(self, document):
        """
        Remove the given document from the index.
        
        document: Document object or document ID number.
        """
        pass

    def get_document(self, doc_id_or_path):
        """Return the Document with the given id or path, or None if not found."""
        pass

    def find_documents(self, *tags):
        """
        Return a set of documents with the given combination of tags.
        
        tags: Tag names or tuples of (tagName, tagValue),
              or Comparison objects from the comparisons module.
        """
        pass

    def add_tag(self, name, numeric=True):
        """Add or overwrite the given tag in the index."""
        pass

    def delete_tag(self, name):
	"""Remove the given tag from the index."""
        pass

    def get_all_tags(self):
        """Return a set of all tag names in the index."""
        pass

    def tag_document(self, document, *tags):
        """
        Assign the given tags or tuples of tags and values
        to the given document ID or Document object.
        """
        pass

    def get_document_tags(self, document):
        """Return a dictionary of tags mapped to values for the given document ID or Document object."""
        pass

