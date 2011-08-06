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
        self.src_file = "/home/mohammed/Desktop/op.txt"
        self.first_dest_file = "/home/mohammed/Desktop/final1.bz2"
        self.second_dest_file = "/home/mohammed/Desktop/final2.bz2"
        self.third_dest_file = "/home/mohammed/Desktop/final3.bz2"
        self.fourth_dest_file = "/home/mohammed/Desktop/final4.bz2"
        self.inf = open(self.src_file, 'r')
        self.src_size = os.path.getsize(self.src_file)
        #the compression type used, needed for
        #decompression to check for the extension.
        self.compression_type = ""
        self.compress_input = True #compress the input or not option

    def test_first_transfer(self):
        '''
        passing the parameter self.compression_type is optional. If you don't
        pass it, the decompression will be determined by the filename extension.
        '''
        endpoint = create_endpoint_entry()
        final = endpoint.create_endpoint_entry(self.host, [self.first_dest_file, self.second_dest_file, self.third_dest_file], self.src_size, True, self.compression_type, rename=False)
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

    def test_second_transfer(self):
        '''
        passing the parameter self.compression_type is optional. If you don't
        pass it, the decompression will be determined by the filename extension.
        '''
        endpoint = create_endpoint_entry()
        final = endpoint.create_endpoint_entry(self.host, [self.second_dest_file], self.src_size, False, self.compression_type, rename=False)
        #final = ["/home/mohammed/Desktop/output2.txt"]
        '''
        self.compression_type is an optional parameter. You can pass it or not.
        If you will pass the self.compression_type, so use:
        c = LTClient(self.src_file, final, self.compression_type)
        If you won't pass it and will depend on the file extension to be
        checked, so use:
        c = LTClient(self.src_file, final)
        '''
        c = LTClient(self.first_dest_file, final)
        v = LTServer(c, c)
        v.store_and_forward()


if __name__ == '__main__':
    unittest.main()


