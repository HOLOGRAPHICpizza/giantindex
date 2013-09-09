import contextlib
import comparisons
import MySQLdb


class Document(object):
    """Immutable document descriptor."""

    def __init__(self, path, modified, size, docID=None):
        if docID:
            self.docID = int(docID)
        else:
            self.docID = None
        self.path = str(path)
        self.modified = long(modified)
        self.size = long(size)


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

#    def pathIsIndexed(self, path):
#        """Return true if the path is in the database, false otherwise."""
#
#        with contextlib.closing(self._db.cursor()) as c:
#            c.execute('SELECT id FROM documents WHERE path = %s', (path,))
#            return c.fetchone() is not None

#    def getDocumentPath(self, docID):
#        """Return the path of the document with the given ID."""
#
#        with contextlib.closing(self._db.cursor()) as c:
#            c.execute('SELECT path FROM documents WHERE id = %s', (docID,))
#            return c.fetchone()[0]

    def add_document(self, document):
        """
        Add or overwrite the given document in the index.
	
	document: Document object or document ID number.
	
	Return the updated document.
        """

        with contextlib.closing(self._db.cursor()) as c:
            c.execute("""
                    INSERT INTO documents (id, path, modified, duration, width, height, size)
                    VALUES (NULL, %s, CURRENT_TIMESTAMP, NULL, NULL, NULL, 0)""", (path,))
            self._db.commit()

            c.execute('SELECT id FROM documents WHERE path = %s', (path,))
            return c.fetchone()[0]
    
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

