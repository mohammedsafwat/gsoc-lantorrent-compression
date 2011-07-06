import bz2
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
        if compression_type.lower() == "bz":
            self._bzip = bz2.BZ2Decompressor()

        raise LTException(511, compression_type)

    def unzip(self, buffer):
        return self._bzip.decompress(buffer)
