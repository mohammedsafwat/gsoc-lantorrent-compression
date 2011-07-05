__author__ = 'bresnaha'

import os
from setuptools import setup, find_packages
import sys


Version = "0.2"

if float("%d.%d" % sys.version_info[:2]) < 2.5:
    sys.stderr.write("Your Python version %d.%d.%d is not supported.\n" % sys.version_info[:3])
    sys.stderr.write("lantorrent requires Python 2.5 or newer.\n")
    sys.exit(1)

setup(name='lantorrent',
      version=Version,
      description='An Open Source network protocol for broadcasting large files.',
      author='Nimbus Development Team',
      author_email='workspace-user@globus.org',
      url='http://www.nimbusproject.org/',
      packages=[ 'pylantorrent', 'pylantorrent.nosetests'],
       entry_points = {
        'console_scripts': [
            'ltdaemon = pylantorrent.daemon:main',
            'ltserver = pylantorrent.server:main',
            'ltrequest = pylantorrent.request:main',
            'ltclient = pylantorrent.client:main',
        ],

      },
      download_url ="http://www.nimbusproject.org/downloads/lantorrent-%s.tar.gz" % (Version),
      keywords = "multicast broadcast network protocol transfer",
      long_description="""
Fast multicast of large files (designed for VM images)
""",
      license="Apache2",
      install_requires = ["simplejson == 2.1", "sqlalchemy == 0.6"],

      include_package_data = True,
#      data_files = test_plans,
      package_data = {},

      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python',
          'Topic :: System :: Clustering',
          'Topic :: System :: Distributed Computing',
          ],
     )

lt_home = os.path.expanduser("~/.lantorrent")
if 'LANTORRENT_HOME' in os.environ:
    lt_home  = os.environ['LANTORRENT_HOME']

ini_template = "etc/lt.ini"
dir = os.path.dirname(__file__)
if dir:
    ini_template = dir + "/" + ini_template
ini_template = os.path.abspath(ini_template)
dst = os.path.abspath(lt_home + "/etc/lt.ini")

print ""
print "======================="
print "Copying the configuration file %s to %s" % (ini_template, dst)
cp_cmd = "cp %s %s" % (ini_template, dst)
rc = os.system(cp_cmd)
if rc != 0:
    raise Exception('Failed to copy the config file %s' % (cp_cmd))


print "Lantorrent is now installed into your python environment.  We recommend using the LANTORRENT_HOME environment variable to specify the location of configuration and log files.  If this env is not set then ~/.lantorrent is used."