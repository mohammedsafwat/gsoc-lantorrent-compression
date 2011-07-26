#!/usr/bin/python
import pylantorrent
import sys
import os
import logging
import traceback
from ConfigParser import SafeConfigParser
from optparse import OptionParser
from optparse import SUPPRESS_HELP

import hmac
try:
    from hashlib import sha1 as sha
    from hashlib import sha256 as sha256
except ImportError:
    import sha
import base64
import uuid
try:
    import json
except ImportError:
    import simplejson as json

class create_endpoint_entry:
    def create_endpoint_entry(self, host, dest_files, data_size, compress_input, compression, port=2893, block_size=128*1024, degree=1, rename=True):
        final = {}
        requests = []
        for df in dest_files:
            ent = {}
            ent['filename'] = df
            ent['rename'] = rename
            ent['id'] = str(uuid.uuid1())
            requests.append(ent)

        final['destinations'] = dest_files
        final['requests'] = requests
        final['host'] = host
        final['port'] = port
        final['block_size'] = block_size
        final['degree'] = degree
        final['length'] = data_size
        final['compression'] = compression
        final['compress_input'] = compress_input
        pylantorrent.log(logging.DEBUG, "dest_files %s" % dest_files)
        pylantorrent.log(logging.DEBUG, "compress_input state %s" % compress_input)
        return final