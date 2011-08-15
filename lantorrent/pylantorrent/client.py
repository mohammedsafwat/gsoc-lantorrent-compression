import os.path
import sys
import os
from socket import *
import logging
import pylantorrent
from pylantorrent.server import LTServer
from pylantorrent.ltException import LTException
import traceback
import uuid
import hashlib
import stat
from decompress import LTCompress
try:
    import json
except ImportError:
    import simplejson as json
    
class LTClient(object):

    def __init__(self, filename, json_header):
        self.data_size = os.path.getsize(filename)
        self.data_file = open(filename, "r")
        self.success_count = 0
        self.md5str = None
        self.comp_obj = None
        self.file_data = True
        self.pau = False
        self.md5er = hashlib.md5()

        self.get_file_extension(filename)

        #get the compression type from header that's passed to json_header
        self.compression_type = json_header['compression']
        #check if the compression option is passed via the command line
        self.compress_input = json_header['compress_input']
        self.client_files_a = json_header['client_files_a']
        pylantorrent.log(logging.INFO, "###client_files_a in client.py %s" % self.client_files_a)

        #usecases for the compression/decompression
        if self.compression_type or self.filename_extension:
            self.temp_compression_type = self.compression_type or self.filename_extension
            pylantorrent.log(logging.DEBUG, "Sent file extension is %s" % self.temp_compression_type)
            
            if self.temp_compression_type == "bz2":
                if self.compress_input == False: #no compression option is passed via the command-line
                    self.mode = 'decompression'
                elif self.compress_input == True: #the compression option is passed via the command-line
                    self.mode = 'pass' #pass the file as it is with no compression or decompression
                    
            if self.temp_compression_type != "bz2":
                if self.compress_input == False:
                    self.mode = 'pass'
                elif self.compress_input == True:
                    if self.temp_compression_type == "gz":
                        self.mode = 'pass'
                    else:
                        self.mode = 'compression'
                        pylantorrent.log(logging.INFO, "####The mode is compression.")
                        try:
                            self.comp_obj = LTCompress()
                            d = self.read()
                            pylantorrent.log(logging.INFO, "###d = self.read() is %s" % d)
                            self.data = self.comp_obj.zip(d)
                            self.comp_obj.flush()
                            pylantorrent.log(logging.INFO, "Compressing the %s file...Zipping.." % self.temp_compression_type)
                            for f in self.client_files_a:
                                pylantorrent.log(logging.INFO, "f in self.client_files_a %s" % f)
                                self.f_stream = open(f, 'w')
                                pylantorrent.log(logging.INFO, "#####f_stream %s" % self.f_stream)
                                self.f_stream.write(self.data)
                                self.temp_compression_type = self.get_file_extension(f)
                                self.data_size = len(self.data)
                                pylantorrent.log(logging.INFO, "####last self.data_size %s" % self.data_size)
                        except LTException:
                            pylantorrent.log(logging.ERROR, "Problem with compression.")

        json_header['length'] = self.data_size
        json_header['mode'] = self.mode
        pylantorrent.log(logging.INFO, "########last self.mode is %s" % self.mode)
        json_header['temp_compression_type'] = self.temp_compression_type
        pylantorrent.log(logging.INFO, "########last self.temp_compression_type is %s" % self.temp_compression_type)
        json_header['client_files_a'] = self.client_files_a
        #encoding
        outs = json.dumps(json_header)
        auth_hash = pylantorrent.get_auth_hash(outs)
        self.header_lines = outs.split("\n")
        self.header_lines.append("EOH : %s" % (auth_hash))
        self.errors = []
        self.complete = {}
        #self.file_data = True
        #self.pau = False
        self.incoming_data = ""

        self.dest = {}
        ld = json_header
        pylantorrent.log(logging.DEBUG, "JSON header in LTClient %s" % ld)

        for req in ld['requests']:
            rid = req['id']
            fname = req['filename']

            # create an object to track the request info
            ep = {}
            ep['host'] = ld['host']
            ep['port'] = ld['port']
            ep['id'] = rid
            ep['filename'] = fname
            ep['emsg'] = "Success was never reported, nor was a specific error"
            self.dest[rid] = ep
        '''
        for d in ld:
            for req in d['requests']:
                rid = req['id']
                fname = req['filename']

                # create an object to track the request info
                ep = {}
                ep['host'] = d['host']
                ep['port'] = d['port']
                ep['id'] = rid
                ep['filename'] = fname  
                ep['emsg'] = "Success was never reported, nor was a specific error"
                self.dest[rid] = ep
        '''
        #self.md5er = hashlib.md5()

    def write_to_client_files(self, d):
        for f in self.client_files_a:
            self.f_stream = open(f, 'w')
            pylantorrent.log(logging.INFO, "#####f_stream %s" % self.f_stream)
            self.f_stream.write(d)

    def get_file_extension(self, filename):
        self.filename_splitted = filename.split('.')
        self.filename_extension_list = self.filename_splitted[-1:]
        self.filename_extension = self.filename_extension_list.pop(0)
        pylantorrent.log(logging.DEBUG, "##File extension is %s" % self.filename_extension)
        return self.filename_extension

    def get_f_stream(self):
        return self.f_stream
        
    def flush(self):
        pass

    def readline(self):
        if len(self.header_lines) == 0:
            return None
        l = self.header_lines.pop(0)
        return l
                            
    def read(self, blocksize=128*1024): #blocksize was 1
        pylantorrent.log(logging.DEBUG, "begin reading.... pau is %s" % (str(self.pau)))

        if self.pau:
            pylantorrent.log(logging.DEBUG, "is pau")
            return None
        pylantorrent.log(logging.DEBUG, "reading.... ")
        if self.file_data:
            d = self.data_file.read(blocksize)
            
            if not d:
                pylantorrent.log(logging.DEBUG, "no more file data")
                self.file_data = False
            else:
                pylantorrent.log(logging.DEBUG, "### data len = %d" % (len(d)))
                self.md5er.update(d)
                return d
                return out_buffer
        pylantorrent.log(logging.DEBUG, "check footer")
        if not self.file_data:
            pylantorrent.log(logging.DEBUG, "getting footer")
            foot = {}
            self.md5str = str(self.md5er.hexdigest()).strip()
            foot['md5sum'] = self.md5str
            d = json.dumps(foot)
            pylantorrent.log(logging.DEBUG, "getting footer is now %s" % (d))
            self.pau = True

        return d

    def close(self):
        self.md5str = str(self.md5er.hexdigest()).strip()
        close(self.data_file)

    def write(self, data):
        self.incoming_data = self.incoming_data + data

    def process_incoming_data(self):
        lines = self.incoming_data.split('\n')
        for data in lines:
            try:
                json_outs = json.loads(data)
                rid = json_outs['id']
                if int(json_outs['code']) == 0:
                    c = self.dest.pop(rid)
                    self.complete[rid] = json_out
                    self.success_count = self.success_count + 1
                else:
                    d = self.dest[rid]
                    d['emsg'] = json_outs
            except Exception, ex:
                pass
        self.incoming_data = ""

    def check_sum(self):
        for rid in self.complete.keys():
            c = self.complete[rid]
            if c['md5sum'] != self.md5str:
                raise Exception("There was data corruption in the chain")

    def get_incomplete(self):
        self.process_incoming_data()
        return self.dest

def main(argv=sys.argv[1:]):
    
    dests = [] 
    cnt = 1
    l = sys.stdin.readline()
    data_size = os.path.getsize(argv[0])
    while l:
        # each line is a url to be broken down
        a = l.split(":", 1)
        if len(a) != 2:
            raise Exception("url %d not properly formatted: %s" % (cnt, l))
        host = a[0]
        l = a[1]
        a = l.split("/", 1)
        if len(a) != 2:
            raise Exception("url %d not properly formatted: %s" % (cnt, l))
        port = a[0]
        x = int(port)
        filename = "/" + a[1].strip()

        filenames = [filename,]
        json_dest = pylantorrent.create_endpoint_entry(host, filenames, data_size, compression, port, block_size, degree)
        dests.append(json_dest)

        l = sys.stdin.readline()
        cnt = cnt + 1

    # for the sake of code resuse this will just be piped into an
    # lt daemon processor.  /dev/null is used to supress a local write
    final = pylantorrent.create_endpoint_entry("localhost", ["/dev/null",], data_size, compression, rename=False)
    final['destinations'] = dests

    c = LTClient(argv[0], final)
    v = LTServer(c, c)
    v.store_and_forward()
    v.clean_up()
    c.close()
    c.check_sum()

    es = c.get_incomplete()
    for k in es:
        e = es[k]
        if e['emsg'] == None:
            e['message'] = "Unknown error.  Please retry"
        else:
            e = e['emsg']
        print "ERROR: %s:%s%s %s" % (e['host'], e['port'], str(e['filename']), e['message'])       
    print "Succesfully sent to %d" % (c.success_count)

    return 0

if __name__ == "__main__":
    if 'LANTORRENT_HOME' not in os.environ:
        msg = "The env LANTORRENT_HOME must be set"
        print msg
        raise Exception(msg)
    rc = main()
    sys.exit(rc)
