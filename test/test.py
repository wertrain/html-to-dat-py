# -*- coding: utf-8 -*-
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + '/lib')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + '/')
from html2dat import perser
import unittest

class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        self.files = []
        for path in ['data/1386326019.html', 'data/1447860021.html', 'data/1467492969.html']:
            file = open(path)
            html = '\n'.join(file.readlines())
            self.files.append(html)
            file.close
    
    def test_version(self):
        for i, html in enumerate(self.files):
            self.assertTrue(i == perser.check_version(html))

    def test_perse(self):
        for i, html in enumerate(self.files):
            self.assertTrue(0 < len(perser.perse(html)))
            
    def test_thread(self):
        for i, html in enumerate(self.files):
            self.assertTrue(perser.get_thread(html) is not None)

if __name__ == '__main__':
    unittest.main()
