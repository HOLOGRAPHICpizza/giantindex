import unittest
import index as gindex
import settings
import time


class DocumentTest(unittest.TestCase):
    def test_constructor(self):
        path, modified, size, docID, added = 'blarg', 1337, 69, 9001, 343

        d = gindex.Document(path, modified, size)
        self.assertEquals(d.path, path)
        self.assertEquals(d.size, size)
        self.assertEquals(d.doc_id, None)

        d = gindex.Document(path, modified, size, docID, added)
        self.assertEquals(d.doc_id, docID)
        self.assertEquals(d.added, added)


class IndexTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cfg = settings.get()
        if cfg is None:
            raise settings.ConfigurationNotFoundException()

        IndexTest.index = gindex.Index(cfg['host'], cfg['user'], cfg['passwd'], cfg['db'])

    @classmethod
    def tearDownClass(cls):
        IndexTest.index.close()

    def test_contains_doc_id(self):
        self.assertTrue(IndexTest.index.contains_doc_id(1), "Index should contain doc_id 1.")

    def test_doc_id_of_path(self):
        doc_id = IndexTest.index.doc_id_of_path('/testpath')
        self.assertEqual(1, doc_id, '/testpath should have doc_id 1')

    def test_add_document(self):
        path = str(time.time())
        doc = gindex.Document(path, 1337, 9001)
        new_doc = IndexTest.index.add_document(doc)

        self.assertEqual(doc.path, new_doc.path)
        self.assertEqual(doc.modified, new_doc.modified)
        self.assertEqual(doc.size, new_doc.size)
        self.assertIsNotNone(new_doc.doc_id)
        self.assertIsNotNone(new_doc.added)

        new_path = path[::-1]
        doc3 = gindex.Document(new_path, doc.modified, doc.size, new_doc.doc_id, new_doc.added)
        doc4 = IndexTest.index.add_document(doc3)

        self.assertEqual(new_path, doc4.path)
        self.assertEqual(doc.modified, doc4.modified)
        self.assertEqual(doc.size, doc4.size)
        self.assertEqual(new_doc.doc_id, doc4.doc_id)
        self.assertEqual(new_doc.added, doc4.added)

if __name__ == '__main__':
    unittest.main()
