__author__ = 'michael'

import unittest
from giantindex.index import *


class DocumentTest(unittest.TestCase):
    def constructor(self):
        path, modified, size, docID = 'blarg', 1337, 69, 9001

        d = Document(path, modified, size)
        self.assertEquals(d.path, path)
        self.assertEquals(d.size, size)
        self.assertEquals(d.docID, None)

        d = Document(path, modified, size, docID)
        self.assertEquals(docID)

if __name__ == '__main__':
    unittest.main()
