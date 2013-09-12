import unittest
import index as gindex
import settings


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

if __name__ == '__main__':
    unittest.main()
