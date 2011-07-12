import bz2
import sys
import pylantorrent
import logging
from pylantorrent.ltException import LTException

class LTCompress(object):

    def __init__(self, level=2):
        self._bzip = bz2.BZ2Compressor(compresslevel=level)

    def zip(self, buffer):
        d = self._bzip.compress(buffer)
        return d

    def flush(self):
        return self._bzip.flush()
        

class LTDecompress(object):
    def __init__(self, compression_type):
        #  here we will pick set the compression object based upon the
        #  type.  Only bz is supported for now.  all others will cause an
        #  error
        if compression_type.lower() == "bz2":
            pylantorrent.log(logging.ERROR, "Yes..the compression type is bz2")
            self._bzip = bz2.BZ2Decompressor()
        else:
            pylantorrent.log(logging.ERROR, "The compression type is not bz2")
            raise LTException(511, "Unknown compression type:", compression_type)
            
    def unzip(self, buffer):
        return self._bzip.decompress(buffer)
