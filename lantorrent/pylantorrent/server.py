#!/usr/bin/python
import sys
import os
from socket import *
import logging
import pylantorrent
from pylantorrent.ltException import LTException
from pylantorrent.ltConnection import *
import simplejson as json
import traceback
import hashlib
from decompress import LTDecompress
from decompress import LTCompress
from pylantorrent.client import LTClient
#  The first thing sent is a json header terminated by a single line
#  of EOH
#
#  {
#      host
#      port
#      length
#      requests = [ {filename, id, rename}, ]
#      destinations =
#       [ {
#           host
#           port
#           requests = [ { filename, id, rename } ]
#           block_size
#       }, ]
#  }
#
class LTServer(object):

    def __init__(self, inf, outf):
        self.inf = inf
        self.json_header = {}
        self.source_conn = LTSourceConnection(inf)
        self.outf = outf
        self.block_size = 128*1024
        self.suffix = ".lantorrent"
        self.created_files = []
        self.v_con_array = []
        self.files_a = []
        self.md5str = None
        self.decomp_obj = None
        self.comp_obj = None
        
    def _close_files(self):
        for f in self.files_a:
            f.close()
        self.files_a = []
        
    def _close_connections(self):
        for v_con in self.v_con_array:
            v_con.close()
        self.v_con_array = []

    def clean_up(self, force=False):
        self._close_connections()
        self._close_files()
        pylantorrent.log(logging.DEBUG, "cleaning up")
        for f in self.created_files:
            try:
                pylantorrent.log(logging.DEBUG, "deleting file %s" % (f))
                # dont delete /dev/null (or any other dev really)
                ndx = f.strip().find("/dev")
                if ndx != 0:
                    os.remove(f)
            except:
                pass
        self.created_files = []

    def _read_footer(self):
        pylantorrent.log(logging.INFO, "beginning _read_footer..")
        pylantorrent.log(logging.INFO, "current source_conn %s" % self.source_conn)
        self.footer = self.source_conn.read_footer(self.md5str)

    def _send_footer(self):
        foot = {}
        foot['md5sum'] = self.md5str
        foot_str = json.dumps(foot)
        pylantorrent.log(logging.DEBUG, "sending footer %s" % (foot_str))
        for v_con in self.v_con_array:
            v_con.send(foot_str)

    def _read_header(self):
        pylantorrent.log(logging.DEBUG, "beginning _read_header()")
        self.json_header = self.source_conn.read_header()
        pylantorrent.log(logging.DEBUG, "##self.source_conn.read_header() %s" % self.json_header)
        self.degree = int(self.json_header['degree'])
        self.data_length = long(self.json_header['length'])
        pylantorrent.log(logging.INFO, "###last self.data_length %s" % self.data_length)
        self.mode = self.json_header['mode']
        self.temp_compression_type = self.json_header['temp_compression_type']
        self.compress_input = self.json_header['compress_input']
        self.client_files_a = self.json_header['client_files_a']
        pylantorrent.log(logging.INFO, "#self.compress_input state in _read_header is %s" % self.compress_input)
        pylantorrent.log(logging.INFO, "#client_files_a in server.py %s" % self.client_files_a)

        if self.compress_input == True:
            for f in self.client_files_a:
                try:
                    self.f_inf = open(f, "r")
                except Exception:
                    print "There was an error opening the f file."
                self.source_conn = LTSourceConnection(self.f_inf)
                pylantorrent.log(logging.INFO, "##self.source_conn in compression mode is %s" % self.source_conn)
                
        if self.mode == 'pass':
            try:
                self.comp_obj = False
                self.decomp_obj = False
                pylantorrent.log(logging.DEBUG, "Passing the %s file as it is." % self.temp_compression_type)
            except:
                pylantorrent.log(logging.ERROR, "Problem when passing the %s file." % self.temp_compression_type)
                
        #if the mode is 'decompression'
        if self.mode == 'decompression':
            try:
                self.decomp_obj = LTDecompress(self.temp_compression_type)
            except LTException:
                pylantorrent.log(logging.ERROR, "Problem with auto-decompression, will write the program compressed.")
                
    def print_results(self, s):
        pylantorrent.log(logging.DEBUG, "printing\n--------- \n%s\n---------------" % (s))
        self.outf.write(s)
        self.outf.flush()
 
    def _get_valid_vcons(self, destinations):
        pylantorrent.log(logging.DEBUG, "Start of _get_valid_vcons")
        v_con_array = []
        
        while len(destinations) > 0 and len(v_con_array) < self.degree:
            ep = destinations.pop(0)
            pylantorrent.log(logging.DEBUG, "ep is %s" % ep)
            try:
                header = self.json_header
                pylantorrent.log(logging.DEBUG, "header in _get_valid_vcons %s" % header)
                v_con = LTDestConnection(header, self)
                v_con_array.append(v_con)
            except LTException, vex:
                # i think this is the only recoverable error
                # keep track of them and return in output
                s = vex.get_printable()
                self.print_results(s)

        each = len(destinations) / self.degree
        rem = len(destinations) % self.degree
        ndx = 0
        for v_con in v_con_array:
            end = ndx + each + rem
            mine = destinations[ndx:end]
            rem = 0
            v_con.send_header(mine)
        self.v_con_array = v_con_array

    def _open_dest_files(self, requests_a):
        pylantorrent.log(logging.INFO, "Opening destination files.")
        files_a = []
        for req in requests_a:
            filename = req['filename']
            try:
                rn = req['rename']
                if rn:
                    filename = filename + self.suffix
                self.f = open(filename, "w")
                files_a.append(self.f)
                self.created_files.append(filename)
            except Exception, ex:
                pylantorrent.log(logging.ERROR, "Failed to open %s" % (filename), traceback)
                raise LTException(503, str(ex), self.json_header['host'], int(self.json_header['port']), reqs=requests_a)
        self.files_a = files_a

    # perhaps this should even be an io event system or threads.  For now
    # it will throttle on the one blocking socket from the data source
    # and push the rest to the vcon objects
    def _process_io(self):
        pylantorrent.log(logging.DEBUG, "Start of _process_io()")
        md5er = hashlib.md5()
        read_count = 0
        bs = self.block_size
        pylantorrent.log(logging.DEBUG, "old inf %s" % self.inf)
        pylantorrent.log(logging.DEBUG, "Outer read_count %s" % read_count)
        while read_count < self.data_length:
            pylantorrent.log(logging.DEBUG, "Inner read_count %s" % read_count)
            pylantorrent.log(logging.DEBUG, "self.data_length %s" % self.data_length)
            if bs + read_count > self.data_length:
                bs = self.data_length - read_count
            data = self.source_conn.read_data(bs)
            if data:
                pylantorrent.log(logging.INFO, "I'm reading data!")
            pylantorrent.log(logging.DEBUG, "data = self.source_conn.read_data(bs) %s" % data)
            read_count = read_count + len(data)
            pylantorrent.log(logging.DEBUG, "read_count = read_count + len(data) %s" % read_count)
            if data == None:
                raise Exception("Data is None prior to receiving full file %d %d" % (read_count, self.data_length))
            if self.compress_input == False:
                md5er.update(data)
            for v_con in self.v_con_array:
                v_con.send(data)
            if self.decomp_obj:
                pylantorrent.log(logging.DEBUG, "Unzipping...")
                data = self.decomp_obj.unzip(data)
            pylantorrent.log(logging.DEBUG, "writing to files...")
            for f in self.files_a:
                f.write(data)
                self.f.close()
            if self.compress_input == True:
                md5er.update(data)
                self.source_conn = LTSourceConnection(self.inf)
        self.md5str = str(md5er.hexdigest()).strip()
        pylantorrent.log(logging.DEBUG, "We have received sent %d bytes. The md5sum is %s" % (read_count, self.md5str))
            
        
    def store_and_forward(self):
        #self._read_footer()
        self._read_header()
        header = self.json_header
        pylantorrent.log(logging.DEBUG, "JSON header in store_and_forward %s" % header)
        requests_a = header['requests']
        self._open_dest_files(requests_a)
        destinations = header['destinations']
        pylantorrent.log(logging.DEBUG, "destinations in store_and_forward %s" % destinations)
        pylantorrent.log(logging.DEBUG, "_get_valid_vcons")
        self._get_valid_vcons(destinations)
        self._process_io()
        pylantorrent.log(logging.DEBUG, "Start of _close_files()")
        # close all open files
        self._close_files()
        # read the footer from the sending machine
        self._read_footer()
        # send foot to all machines this is streaming to
        self._send_footer()
        # wait for eof and close
        self._close_connections()
        self._rename_files(requests_a)

        pylantorrent.log(logging.DEBUG, "All data sent %s %d" % (self.md5str, len(requests_a)))
        # if we got to here it was successfully written to a file
        # and we can call it success.  Print out a success message for 
        # everyfile written
        vex = LTException(0, "Success", header['host'], int(header['port']), requests_a, md5sum=self.md5str)
        s = vex.get_printable()
        self.print_results(s)
        #self.clean_up()

    def _rename_files(self, requests_a):
        for req in requests_a:
            realname = req['filename']
            rn = req['rename']
            if rn:
                tmpname = realname + self.suffix
                pylantorrent.log(logging.DEBUG, "renaming %s -> %s" % (tmpname, realname))

                os.rename(tmpname, realname)
                self.created_files.remove(tmpname)


def main(argv=sys.argv[1:]):

    pylantorrent.log(logging.INFO, "server starting")
    rc = 1
    v = LTServer(sys.stdin, sys.stdout)
    try:
        v.store_and_forward()
        rc = 0
    except LTException, ve:
        pylantorrent.log(logging.ERROR, "error %s" % (str(ve)), traceback)
        s = ve.get_printable()
        v.print_results(s)
        v.clean_up()
    except Exception, ex:
        pylantorrent.log(logging.ERROR, "error %s" % (str(ex)), traceback)
        vex = LTException(500, str(ex))
        s = vex.get_printable()
        v.print_results(s)
        v.clean_up()

    return rc

if __name__ == "__main__":
    if 'LANTORRENT_HOME' not in os.environ:
        msg = "The env LANTORRENT_HOME must be set"
        print msg
        raise Exception(msg)

    rc = main()
    sys.exit(rc)

