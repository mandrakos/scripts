#!/usr/bin/env python3

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
   parser.add_argument('--no-pics', action='store_true')
   parser.add_argument('--no-movies', action='store_true')
   parser.add_argument('--no-raw', action='store_true')

   skipdirs = ['.streams','.@__thumb','@Recycle']

   args = parser.parse_args()
   searchpath = args.searchpath
   picsavdir = args.picsavdir
   rawsavdir = picsavdir+'/raw/'
   movsavdir = picsavdir+'/movies/'
 
   # jhead moves the photos (not copy), so use a temporary directory in case something
   # goes horribly awry. Separately we'll use fdupes to remove pictures from searchpath.
   pictmpdir = '/share/homes/john/photo_xfer/organize_photos'
   rawtmpdir = '/share/homes/john/photo_xfer/raw'
   movtmpdir = '/share/homes/john/photo_xfer/movies'

   # move JPG files to temp and rename with time stamp
   for d in [pictmpdir, rawtmpdir, movtmpdir]:
      mkdir_p(d)

   picfiles = []
   cr2files = []
   movfiles = []

   for dirpath, dirnames, filenames in os.walk(searchpath):
      # if there are no filenames there's nothing to do
      if filenames:
         # ignore files in thumbnail and recycle dirs
         if not any (s in dirpath for s in skipdirs):
            print(dirpath)
            # find jpg, case insensitive
            if not args.no_pics:
               for filename in fnmatch.filter(filenames, '*.[Jj][Pp][Gg]'):
                  mkdir_p(pictmpdir+'/'+dirpath)
                  fullname = os.path.join(dirpath,filename)
                  copiedfile = pictmpdir+'/'+dirpath+'/'+filename.replace(" ","_")
                  picfiles.append(copiedfile)
                  shutil.copyfile(fullname, copiedfile)  
             
            # find cr2 raw, case insensitive
            if not args.no_raw:
               for filename in fnmatch.filter(filenames, '*.[Cc][Rr][2]'):
                  mkdir_p(rawtmpdir+'/'+dirpath)
                  fullname = os.path.join(dirpath,filename)
                  copiedfile = rawtmpdir+'/'+dirpath+'/'+filename.split('/')[-1].split('.')[0]+'.CR2'
                  copiedfile = copiedfile.replace(" ","_")
                  cr2files.append(copiedfile)
                  shutil.copyfile(fullname, copiedfile)  

            # find movie files
            if not args.no_movies:
               regexes = ['*.[Mm][Oo][Vv]','*.[Mm][Pp][4]']
               for regex in regexes:
                  for filename in fnmatch.filter(filenames, regex):
                     mkdir_p(movtmpdir+'/'+dirpath)
                     fullname = os.path.join(dirpath,filename)
                     copiedfile = movtmpdir+'/'+dirpath+'/'+filename.replace(" ","_")
                     movfiles.append(copiedfile)
                     shutil.copyfile(fullname, copiedfile)  

                  
   # use jhead to move to date specific directory
   # cmd can't be a list, and must use shell=True
   if picfiles:
      jheadcmd = ['jhead','-autorot','-n'+picsavdir+'/%Y/%m/%f'] +picfiles
      subprocess.call(jheadcmd)

   if cr2files:
      # use exiftool to get created date for year/month directory structure
      out = subprocess.check_output(['exiftool','-createdate']+cr2files).split('\n')[:-2]

      names = [ f.split(' ')[-1] for f in out[0::2] ]
      year =  [ f.split(':')[1].strip() for f in out[1::2] ]
      month = [ f.split(':')[2].strip() for f in out[1::2] ]

      for i in range(0,len(names)):
        d = '/'.join([rawsavdir,year[i],month[i]])
        mkdir_p(d)
        shutil.copy(names[i], d)

   #Now any movie files
   if movfiles:
      # use exiftool to get created date for year/month directory structure
      out = subprocess.check_output(['exiftool','-config','/share/homes/john/scripts/config.exiftool','-createdate']+movfiles).split('\n')[:-2]

      names = [ f.split(' ')[-1] for f in out[0::2] ]
      year =  [ f.split(':')[1].strip() for f in out[1::2] ]
      month = [ f.split(':')[2].strip() for f in out[1::2] ]

      for i in range(0,len(names)):
        d = '/'.join([movsavdir,year[i],month[i]])
        mkdir_p(d)
        shutil.copy(names[i], d)


def main(argv=None):

   check_if_running()
   try:
      with open(pidfile, 'w') as out:
         out.write(str(os.getpid()))
      organize_photos()
   finally:
      os.unlink(pidfile)
   
   
if __name__ == "__main__":
   sys.exit(main())
   
