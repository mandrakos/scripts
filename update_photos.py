#!/usr/bin/env python

from __future__ import print_function
import sys
import fnmatch
import os
import shutil
import argparse
import subprocess

pidfile = "/tmp/update_photos.pid"

def mkdir_p(dirname):

   if not os.path.exists(dirname):
      try:
         os.makedirs(dirname)
      except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
           pass
        else:
           raise

def check_if_running():

   if os.path.isfile(pidfile):
      print("%s already exists, exiting" % pidfile)
      sys.exit()
   
def organize_photos():
   argv = sys.argv

   parser = argparse.ArgumentParser()
   parser.add_argument('searchpath', metavar='search-path')
   parser.add_argument('picsavdir', metavar='out-dir')

   skipdirs = ['.@__thumb','@Recycle']

   args = parser.parse_args()
   searchpath = args.searchpath
   picsavdir = args.picsavdir
 
   # jhead moves the photos (not copy), so use a temporary directory in case something
   # goes horribly awry. Separately we'll use fdupes to remove pictures from searchpath.
   pictmpdir = '/share/homes/john/photo_xfer/organize_photos'
   rawtmpdir = '/share/homes/john/photo_xfer/raw'
   rawsavdir = '/share/pictures/raw'

   # move JPG files to temp and rename with time stamp
   for d in [pictmpdir, rawtmpdir]:
      mkdir_p(d)

   for dirpath, dirnames, filenames in os.walk(searchpath):
      # if there are no filenames there's nothing to do
      print(dirpath)

      if filenames:
         # ignore files in thumbnail and recycle dirs
         parentdir = dirpath.split('/')[-1]
         if parentdir not in skipdirs:

            # find jpg, case insensitive
            for filename in fnmatch.filter(filenames, '*.[Jj][Pp][Gg]'):

               fullname = os.path.join(dirpath,filename)
               # copy to tmp dir
               shutil.copy(fullname, pictmpdir)  
             
            # find cr2 raw, case insensitive
            for filename in fnmatch.filter(filenames, '*.[Cc][Rr]2'):
               fullname = os.path.join(dirpath,filename)
               newfullname = fullname.split('/')[-1].split('.')[0]+'.CR2'
               shutil.copyfile(fullname, newfullname)  
                  
   # use jhead to move to date specific directory
   # cmd can't be a list, and must use shell=True
   jheadcmd = 'jhead -autorot -n'+picsavdir+'/%Y/%m/%f '+pictmpdir+'/*'
   subprocess.call(jheadcmd, shell=True)

   # use exiftool to get created date for year/month directory structure
   out = subprocess.check_output('exiftool -createdate '+rawtmpdir+'/*.CR2', shell=True).split('\n')[:-2]

   names = [ f.split(' ')[-1] for f in out[0::2] ]
   year =  [ f.split(':')[1].strip() for f in out[1::2] ]
   month = [ f.split(':')[2].strip() for f in out[1::2] ]

   for i in range(0,len(names)):
     d = '/'.join([picsavdir,year[i],month[i],'raw'])
     mkdir_p(d)
     shutil.copy(names[i], d)

   #Now any movie files


   

def main(argv=None):

   check_if_running()
   try:
      file(pidfile, 'w').write(str(os.getpid()))
      organize_photos()
   finally:
      os.unlink(pidfile)
   
   
if __name__ == "__main__":
   sys.exit(main())
   
