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
        self.src_file = "/home/mohammed/Desktop/easymock-3.0.zip"
        self.src_size = os.path.getsize(self.src_file)
        self.compression_type = "bz2"
        
    def test_decompression(self):
        '''
        passing the parameter self.compression_type is optional. If you don't
        pass it, the compression will be determined by the filename extension.
        '''
        final = pylantorrent.create_endpoint_entry(self.host, ["/home/mohammed/Desktop/patch.txt"], self.src_size, rename=False)
        final['destinations'] = []
        '''
        self.compression_type is an optional parameter. You can pass it or not.
        If you will pass the self.compression_type, so use:
        c = LTClient(self.src_file, final, self.compression_type)
        If you won't pass it and will depend on the file extension to be
        checked, so use:
        c = LTClient(self.src_file, final)
        '''
        c = LTClient(self.src_file, final)
        v = LTServer(c, c)
        v.store_and_forward()
        
if __name__ == '__main__':
    unittest.main()

        
