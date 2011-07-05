#!/usr/bin/python
import sys
from decompress import LTCompress

def main():

    infilename = sys.argv[1]
    outfilename = sys.argv[2]
    buffer_size = 1024*64

    comp = LTCompress()

    inf = open(infilename, "r")
    outf = open(outfilename, "w")
    buffer = inf.read(buffer_size)
    while buffer:
        out_buffer = comp.zip(buffer)
        outf.write(out_buffer)
        buffer = inf.read(buffer_size)
    out_buffer = comp.flush()
    outf.write(out_buffer)

    inf.close()
    outf.close()

    return 0

if __name__ == "__main__":
  rc = main()
  sys.exit(rc)


  
