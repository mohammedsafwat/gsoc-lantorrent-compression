import bz2

class LTCompress(object):

    def __init__(self, level=2):
        self._bzip = bz2.BZ2Compressor(compresslevel=level)

    def zip(self, buffer):
        d = self._bzip.compress(buffer)
        return d

    def flush(self):
        return self._bzip.flush()
        

class LTDecompress(object):

    def __init__(self):
        self._bzip = bz2.BZ2Decompressor()

    def unzip(self, buffer):
        return self._bzip.decompress(buffer)
