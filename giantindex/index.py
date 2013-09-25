import contextlib
import MySQLdb
import os


class Document(object):
    """Immutable document descriptor."""

    def __init__(self, path, modified, size, doc_id=None, added=None, new=False):
        if doc_id is not None:
            self.doc_id = int(doc_id)
        else:
            self.doc_id = None

        if added is not None:
            self.added = long(added)
        else:
            self.added = None

        self.path = os.path.abspath(str(path))
        self.modified = long(modified)
        self.size = long(size)
        self.new = new is True

    def __eq__(self, other):
        return self.doc_id == other.doc_id


class IndexPathConflictException(Exception):
    def __init__(self, path, doc_id):
        self.path = path
        self.doc_id = doc_id

    def __str__(self):
        return "'%s' is already indexed under ID %i." % (self.path, self.doc_id)


class InvalidDocumentException(Exception):
    def __init(self, msg):
        self.msg = str(msg)

    def __str__(self):
        return self.msg


class InvalidTagException(Exception):
    def __init__(self, msg):
        self.msg = str(msg)

    def __str__(self):
        return self.msg


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

    def cursor(self):
        return contextlib.closing(self.db.cursor())

    def contains_doc_id(self, doc_id):
        """Returns True if a document has this ID, False otherwise."""
        with self.cursor() as c:
            c.execute('SELECT id FROM documents WHERE id = %s', (int(doc_id),))
            return c.fetchone() is not None

    def doc_id_of_path(self, path):
        """Returns the ID of the document with this path if one exists, or None otherwise."""
        with self.cursor() as c:
            c.execute('SELECT id FROM documents WHERE path = %s', (os.path.abspath(str(path)),))
            row = c.fetchone()
            if row is not None:
                return int(row[0])
            else:
                return None

    def add_document(self, document):
        """
        Add or overwrite the given document in the index.
        document: Document object

        Return the updated document.

        Raises IndexPathConflictException if document.path is non-unique in the index.
        """
        with self.cursor() as c:
            path_doc_id = self.doc_id_of_path(str(document.path))

            doc_id = document.doc_id
            if document.doc_id is None:
                doc_id = path_doc_id

            # Is an on-file doc_id specified?
            if doc_id is not None and self.contains_doc_id(doc_id):
                # Update Document

                # check for path conflicts
                # must be no docs with path or only this doc
                if path_doc_id is None or path_doc_id == doc_id:
                    # update db
                    c.execute('UPDATE documents SET path = %s, modified = FROM_UNIXTIME(%s), size = %s WHERE id = %s',
                             (document.path, long(document.modified), document.size, doc_id))
                else:
                    raise IndexPathConflictException(document.path, path_doc_id)

            else:
                # Insert Document

                document.new = True

                # check for path conflicts
                if path_doc_id is not None:
                    raise IndexPathConflictException(document.path, path_doc_id)

                # insert to db new with generated id
                c.execute("""
                         INSERT INTO documents (id, path, added, modified, size)
                         VALUES (DEFAULT, %s, UNIX_TIMESTAMP(CURRENT_TIMESTAMP), %s, %s)""",
                         (document.path, document.modified, document.size))
        self.db.commit()

        with self.cursor() as c:
            # select new document object
            c.execute("SELECT id, added FROM documents WHERE path = %s", (document.path,))
            row = c.fetchone()
            return Document(
                document.path,
                document.modified,
                document.size,
                row[0],
                row[1],
                new=document.new)
    
    def remove_document(self, document):
        """
        Remove the given document from the index.
        
        document: Document object or document ID number.
        """
        doc_id = None
        if isinstance(document, Document):
            doc_id = int(document.doc_id)
        else:
            doc_id = int(document)

        if doc_id is None:
            raise InvalidDocumentException('No document ID given.')

        with self.cursor() as c:
            c.execute("DELETE FROM documents WHERE ID = %s", (doc_id,))
        self.db.commit()

    def get_document(self, doc_id_or_path):
        """Return the Document with the given id or path, or None if not found."""
        doc_id = None
        path = None
        try:
            int(doc_id_or_path)
            doc_id = int(doc_id_or_path)
        except ValueError:
            path = os.path.abspath(str(doc_id_or_path))

        with self.cursor() as c:
            if doc_id is not None:
                c.execute("SELECT * FROM documents WHERE id = %s", (doc_id,))

            else:
                c.execute("SELECT * FROM documents WHERE path = %s", (path,))

            row = c.fetchone()

            if row is not None:
                return Document(
                    row[1],
                    row[3],
                    row[4],
                    doc_id=row[0],
                    added=row[2])
            else:
                return None

    def find_documents(self, *tags):
        """
        Return a set of documents with the given combination of tags.
        
        tags: Tag names or tuples of (tagName, tagValue),
              or Comparison objects from the comparisons module.
        """
        num_tags = set()
        str_tags = set()
        nullval_tags = set()
        for tag in tags:
            if not isinstance(tag, str):
                tag_name = str(tag[0])

                numeric = False
                with self.cursor() as c:
                    c.execute("SELECT `numeric` FROM tags WHERE name = %s", (tag_name,))
                    row = c.fetchone()
                    if row is not None:
                        numeric = int(row[0]) == 1
                    else:
                        raise InvalidTagException("% is not a valid tag." % (tag_name,))

                if numeric:
                    num_tags.add((tag_name, int(tag[1])))
                else:
                    str_tags.add((tag_name, str(tag[1])))

            else:
                nullval_tags.add(str(tag))

        docs = set()
        #TODO: verfiy this works
        for tag in nullval_tags:
            with self.cursor() as c:
                c.execute("""
                         SELECT id, path, added, modified, size
                         FROM documents, tags, document_tags
                         WHERE tags.name = %s AND tags.id = document_tags.tag AND tags.document = documents.id""",
                         (tag,))
                matches = set()
                rows = c.fetchall()
                for row in rows:
                    matches.add(Document(row[1], row[3], row[4], row[0], row[2]))
                docs = docs.intersection(docs, matches)
        for tag, value in str_tags:
            with self.cursor() as c:
                c.execute("""
                         SELECT id, path, added, modified, size
                         FROM documents, tags, document_tags
                         WHERE tags.name = %s AND tags.id = document_tags.tag AND document_tags.string_value = %s AND tags.document = documents.id""",
                         (tag, value))
                matches = set()
                rows = c.fetchall()
                for row in rows:
                    matches.add(Document(row[1], row[3], row[4], row[0], row[2]))
                docs = docs.intersection(docs, matches)
        for tag, value in num_tags:
            with self.cursor() as c:
                c.execute("""
                         SELECT id, path, added, modified, size
                         FROM documents, tags, document_tags
                         WHERE tags.name = %s AND tags.id = document_tags.tag AND document_tags.int_value = %s AND tags.document = documents.id""",
                         (tag, value))
                matches = set()
                rows = c.fetchall()
                for row in rows:
                    matches.add(Document(row[1], row[3], row[4], row[0], row[2]))
                docs = docs.intersection(docs, matches)

        return docs

    def add_tag(self, name, numeric=True):
        """Add or overwrite the given tag in the index."""
        with self.cursor() as c:
            num = 1
            if not numeric:
                num = 0

            c.execute("""
                    INSERT INTO tags (id, name, `numeric`)
                    VALUES (DEFAULT, %s, %s)""",
                      (str(name), num))
        self.db.commit()

        with self.cursor() as c:
            c.execute('SELECT id FROM tags WHERE name = %s', (str(name),))
            return c.fetchone()[0]

    def delete_tag(self, name):
        """Remove the given tag from the index."""
        with self.cursor() as c:
            c.execute("DELETE FROM tags WHERE name = %s", (str(name),))
        self.db.commit()

    def get_all_tags(self):
        """Return a set of all tag names in the index."""
        with self.cursor() as c:
            c.execute('SELECT name FROM tags')
            tags = set()
            rows = c.fetchall()
            for row in rows:
                tags.add(row[0])
            return tags

    def tag_document(self, document, *tags):
        """
        Assign the given tags or tuples of tags and values
        to the given document ID or Document object.
        """
        doc_id = None
        if isinstance(document, Document):
            doc_id = int(document.doc_id)
        else:
            doc_id = int(document)

        if doc_id is None:
            raise InvalidDocumentException('No document ID given.')

        for tag in tags:
            with self.cursor() as c:
                str_val = int_val = 'NULL'
                tag_id = None
                numeric = False

                if isinstance(tag, str):
                    tag_name = str(tag)
                else:
                    tag_name = str(tag[0])
                    if numeric:
                        int_val = int(tag[1])
                    else:
                        str_val = str(tag[1])
                edsfg  c.execute("SELECT id, `numeric` FROM tags WHERE name = %s", (tag_name,))
                row = c.fetchone()
                if row is not None:
                    tag_id = int(row[0])
                    if int(row[1]) == 1:
                        numeric = True
                else:
                    raise InvalidTagException("%s is not a valid tag." % tag_name)

                #TODO: verify this works
                c.execute("""
                         INSERT INTO document_tags (tag, document, string_value, int_value)
                         VALUES (%s, %s, %s, %s)""",
                         (tag_id, doc_id, str_val, int_val))

            self.db.commit()

    def get_document_tags(self, document):
        """Return a dictionary of tags mapped to values for the given document ID or Document object,"""
        doc_id = None
        if isinstance(document, Document):
            doc_id = int(document.doc_id)
        else:
            doc_id = int(document)

        if doc_id is None:
            raise InvalidDocumentException('No document ID given.')

        with self.cursor() as c:
            tags = {}

            c.execute("""
                     SELECT name, numeric, string_value, int_value
                     FROM tags, document_tags
                     WHERE document_tags.document = %s AND tags.id = document_tags.tag""",
                     (doc_id,))
            rows = c.fetchall()
            if rows is not None:
                for row in rows:
                    tag_name = str(row[0])
                    numeric = int(row[1]) == 1
                    value = None
                    if numeric and row[3] is not None and str(row[3]) != 'NULL':
                        value = int(row[3])
                    elif row[2] is not None and str(row[2]) != 'NULL':
                        value = str(row[2])

                    tags[tag_name] = value

            return tags
