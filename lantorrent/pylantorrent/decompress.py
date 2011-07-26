import bz2
import sys
import pylantorrent
import logging
from pylantorrent.ltException import LTException

class LTCompress(object):

    def __init__(self, level=2):
        self._bzip = bz2.BZ2Compressor(compresslevel=level)

    def zip(self, buffer):
        if buffer:
            pylantorrent.log(logging.DEBUG, "buffer is %s" % buffer)
            #d = self._bzip.compress(buffer)
            d = bz2.compress(buffer)
        else:
            pylantorrent.log(logging.DEBUG, "Buffer is empty.")
        if d:
            pylantorrent.log(logging.DEBUG, "d = self._bzip.compress(test) is %s" % d)
        else:
            pylantorrent.log(logging.DEBUG, "d is empty.")
        return d

    def flush(self):
        return self._bzip.flush()
        

class LTDecompress(object):
    def __init__(self, compression_type):
        #  here we will pick set the compression object based upon the
        #  type.  Only bz is supported for now.  all others will cause an
        #  error
        if compression_type.lower() == "bz2":
            pylantorrent.log(logging.ERROR, "Yes..the compression type is %s" % compression_type)
            self._bzip = bz2.BZ2Decompressor()
        else:
            pylantorrent.log(logging.ERROR, "The compression type is not bz2. It's %s" % compression_type)
            raise Exception("Unknown compression type %s", compression_type.lower())
            
    def unzip(self, buffer):
        try:
            return self._bzip.decompress(buffer)
        except EOFError:
            return ''

