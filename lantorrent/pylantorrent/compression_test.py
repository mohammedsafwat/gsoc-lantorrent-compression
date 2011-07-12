#!/usr/bin/python
import os.path
import unittest
import nose.tools
import sys
from client import *
from server import *
from ltConnection import *

class CompressionTest(unittest.TestCase):

    def setUp(self):
        self.host = "localhost"
        #src file for compression
        self.compression_src_file = "/home/mohammed/Desktop/log.txt.bz2"
        self.compression_src_size = os.path.getsize(self.compression_src_file)
        self.compression_type = ""
        #if sys.argv[1] == "-c":
            #self.compress_input = True
        self.compress_input = False
        
    def test_compression(self):
        final = pylantorrent.create_endpoint_entry(self.host, ["/home/mohammed/Desktop/log.txt"], self.compression_src_size, self.compress_input, rename=False)
        final['destinations'] = []
        c = LTClient(self.compression_src_file, final)
        v = LTServer(c, c)
        v.store_and_forward()

if __name__ == '__main__':
    unittest.main()