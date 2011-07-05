import os.path
import unittest
from pylantorret.client import *
from pylantorrent.server import *

class TestSimple(unittest.TestCase):
    def setUp(self):
        self.src_file = '~/Desktop/compression-test3.txt.bz2'
        self.src_size = os.path.getsize(self.src_file)
        self.compression_type = 'bz2'

    def tearDown(self):
        pass

    def testDecompression(self):
        final = pylantorrent.create_endpoint_entry(self.host, ["~/Desktop/compression-test3-output.txt"], self.src_size, self.compression_type, rename=False)
        final['destinations'] = []
        c = LTClient(self.src_final, final)
        v = LTServer(c, c)
        v.store_and_forward()
        
