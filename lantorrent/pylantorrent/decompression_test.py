#!/usr/bin/python
import os.path
import unittest
import nose.tools
import sys
from client import *
from server import *
from ltConnection import *
from create_endpoint_entry import *

class DecompressionTest(unittest.TestCase):
    
    def setUp(self):
        self.host = "localhost"
        #src file for decompression
        self.src_file = "/home/mohammed/Desktop/one.txt"
        self.dest_file = "/home/mohammed/Desktop/output2.txt"
        self.client_files_a = ["/home/mohammed/Desktop/cf1.txt.bz2"]
        self.inf = open(self.src_file, 'r')
        self.src_size = os.path.getsize(self.src_file)
        #the compression type used, needed for
        #decompression to check for the extension.
        self.compression_type = ""
        self.compress_input = True #compress the input or not option
        
    def test_decompression(self):   
        '''
        passing the parameter self.compression_type is optional. If you don't
        pass it, the decompression will be determined by the filename extension.
        '''
        endpoint = create_endpoint_entry()
        final = endpoint.create_endpoint_entry(self.host, self.client_files_a, ["/home/mohammed/Desktop/op3.txt"], self.src_size, self.compress_input, self.compression_type, rename=False)
        #final = ["/home/mohammed/Desktop/output2.txt"]
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

        
