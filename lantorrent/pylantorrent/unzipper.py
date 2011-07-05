#!/usr/bin/python
import sys
from decompress import LTDecompress

def main():

    infilename = sys.argv[1]
    outfilename = sys.argv[2]
    buffer_size = 1024*64

    decomp = LTDecompress()

    inf = open(infilename, "r")
    outf = open(outfilename, "w")
    buffer = inf.read(buffer_size)
    while buffer:
        out_buffer = decomp.unzip(buffer)
        outf.write(out_buffer)
        buffer = inf.read(buffer_size)

    inf.close()
    outf.close()

    return 0

if __name__ == "__main__":
  rc = main()
  sys.exit(rc)

