#!/usr/bin/python
import os.path
import unittest
import nose.tools
import sys
from client import *
from server import *
from ltConnection import *

class DecompressionTest(unittest.TestCase):
    
    def setUp(self):
        self.host = "localhost"
        #src file for decompression
        self.src_file = "/home/mohammed/Desktop/test.txt.zip"
        self.src_size = os.path.getsize(self.src_file)
        #the compression type used, needed for
        #decompression to check for the extension.
        self.compression_type = ""
        self.compress_input = False #compress the input or not option
        
    def test_decompression(self):   
        '''
        passing the parameter self.compression_type is optional. If you don't
        pass it, the decompression will be determined by the filename extension.
        '''
        final = pylantorrent.create_endpoint_entry(self.host, ["/home/mohammed/Desktop/output.txt.zip"], self.src_size, self.compress_input, rename=False)
        final['destinations'] = []
        final['compress_input'] = [self.compress_input]
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

        
