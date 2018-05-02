#!/usr/bin/env python

from __future__ import print_function
import sys
import fnmatch
import os
import shutil
import argparse
import subprocess

pidfile = "/tmp/update_photos.pid"

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
      if not os.path.exists(d):
         try:
            os.makedirs(d)
         except OSError as exc:  # Python >2.5
           if exc.errno == errno.EEXIST and os.path.isdir(path):
              pass
           else:
              raise

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
               # if there is a matching CR2 raw file, move that as well
               # This if for Canon Raw files, if ever get new model camera
               # would have to update extension
               for ext in ['.CR2','.cr2'] :
                  try:
                     # replace jpg extension with CR2 extension and try to copy
                     stripext = fullname.split('.')[:-1]
                     newfull = '.'.join(stripext)+ext
                     shutil.copy(newfull, rawtmpdir)  
                  except:
                     pass
                  
   # use jhead to move to date specific directory
   # cmd can't be a list, and must use shell=True
   jheadcmd = 'jhead -autorot -n'+picsavdir+'/%Y/%m/%f '+pictmpdir+'/*'
   subprocess.call(jheadcmd, shell=True)

   
   #Now any movie files
   
   #
   #if [ $? -eq 0 ]
   #then
   #   rm $PICTMPDIR/*
   #   rm $RAWTMPDIR/*
   #fi
   #rsync -vri --backup --include=*.jpg $/ /home/mandrake/Pictures/

def main(argv=None):

   check_if_running()
   try:
      file(pidfile, 'w').write(str(os.getpid()))
      organize_photos()
   finally:
      os.unlink(pidfile)
   
   
if __name__ == "__main__":
   sys.exit(main())
   
