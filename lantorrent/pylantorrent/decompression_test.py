#!/usr/bin/python
import os.path
import unittest
import nose.tools
from client import *
from server import *
from ltConnection import *

class DecompressionTest(unittest.TestCase):
    
    def setUp(self):
        self.host = "localhost"
        self.src_file = "/home/mohammed/Desktop/patch.txt.bz2"
        self.src_size = os.path.getsize(self.src_file)
        self.compression_type = "bz2"
        
    def test_decompression(self):
        final = pylantorrent.create_endpoint_entry(self.host, ["/home/mohammed/Desktop/patch.txt"], self.src_size, self.compression_type, rename=False)
        final['destinations'] = []
        c = LTClient(self.src_file, final, self.compression_type)
        v = LTServer(c, c)
        v.store_and_forward()
        
if __name__ == '__main__':
    unittest.main()

        
