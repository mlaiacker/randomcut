#!/usr/local/bin/python2.7
# encoding: utf-8
'''
randomcut -- create random movies from videoclips

randomcut is a a first try with moviepy

It defines classes_and_methods

@author:     mlaiacker

@copyright:  2020 mlaiacker. All rights reserved.

@license:    GPL3

@contact:    post@mlaiacker.de
@deffield    updated: Updated
'''

import sys
import os
from pathlib import Path

from datetime import datetime


import glob
#from moviepy.editor import *

import random
import moviepy.editor as mp
import moviepy.video.fx.all as vfx

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2020-12-18'
__updated__ = '2020-12-18'

DEBUG = 1
TESTRUN = 0
PROFILE = 0

class RandomCut:
    def __init__(self):
        self.verbose = 2
        self.glob_patterns = list()
        self.directroy = Path(".")
        self.movie_length = 0 # desired overall length
        self.movie_random = 0 # random filename order
        self.clip_length = 5 # default length of each clip
        self.clip_length_random = 3 # random range for clip length
        self.clip_offset = 1 # from beginning
        self.clip_all = True # use all available clips found
        self.clips_max_n = 300
        self.movie_width = 1280
        self.movie_height = 720 
        self.movie_fps = 30
            

    def addPattern(self, pattern:str):
        self.glob_patterns.append(pattern)
        
    def setDir(self, directory_name:str):
        self.directroy = Path(directory_name)
        
    def setMaxClips(self, n:int):
        if n>1:
            self.clips_max_n = n
    def setClipLength(self, l:int):
        if l :
            if l>0:
                self.clip_length = l
                self.clip_length_random = l*0.5
        
    def findClips(self):
        self.clips_filenames = list()
        for pattern in self.glob_patterns:
            p= str(self.directroy) + "/" + pattern
            filenames = glob.glob(p, recursive=True)
            for f in filenames:
                self.clips_filenames.append(str(Path(f)))
        self.clips_filenames.sort()
        #print(self.clips_filenames)
        
    def cut(self):
        clips = []
        movie_total = 0.0        
        n = 0        
        if self.clip_offset<0:
            self.clip_offset = 0
        if self.clip_length<=0:
            self.clip_length = 1
             
        subtitle = ""
        clips_filenames =  self.clips_filenames.copy()
        if self.movie_random:
            random.shuffle(clips_filenames)            
        for clip_name in clips_filenames:
            try:
                clip = mp.VideoFileClip(str(clip_name), target_resolution=(self.movie_height, self.movie_width))
            except Exception as e:
                if self.verbose>0:
                    print(str(clip_name),e)
                continue
            if clip.duration<self.clip_length*1.5+self.clip_offset:
                if self.verbose>1:
                    print(str(clip_name)," too short:", clip.duration, "s")
                clip.close()
                continue
            if clip.aspect_ratio<1:
                if self.verbose>1:
                    print(str(clip_name)," skip vertical video", clip.aspect_ratio)
                clip.close()
                continue
            if clip.w<640: #self.movie_width:
                if self.verbose>1:
                    print(str(clip_name)," clip too narrow", clip.w)
                clip.close()
                continue
            if clip.h<480:#self.movie_height:
                if self.verbose>1:
                    print(str(clip_name)," clip too small", clip.h)
                clip.close()
                continue
            if clip.fps<20:
                if self.verbose>1:
                    print(str(clip_name)," clip wrong fps", clip.fps)
                clip.close()
                continue
                
            length = self.clip_length
            if self.clip_length_random>0:
                r = self.clip_length_random
                if r > self.clip_length:
                    r = self.clip_length -1
                if r>=1:
                    length = random.randint(int(self.clip_length-r), int(self.clip_length+r))
                if length == 0:
                    length = 1
            start = 0
            if length > clip.duration - self.clip_offset:
                length = clip.duration - self.clip_offset
            else:
                start = random.randint(int(self.clip_offset), int(clip.duration- length))
            if self.verbose>0:
                print(clip_name, int(clip.duration), start,  length)
            clips.append(clip.subclip(start, start + length))
#            clips.append(clip.resize(height=self.movie_height).subclip(start, start + length))
#            clips.append(clip.fx(vfx.resize, height=self.movie_height).subclip(start, start + length))
            subtitle += str(n+1)+"\n"
            movie_total_end = movie_total + length
            subtitle += "{:02d}:{:02d}:{:02d} --> {:02d}:{:02d}:{:02d}\n".format(int(movie_total/60/60), int(movie_total/60%60), int(movie_total%60),
                                                                                 int(movie_total_end/60/60), int(movie_total_end/60%60), int(movie_total_end%60))
            subtitle += str(clip_name)+"\n\n"
            movie_total += length
            if n+1>= self.clips_max_n:
                break
            n+=1
        
        collection = Path(self.directroy).resolve().stem
        if collection !="":
            collection = "_"+collection
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d_%H-%M-%S")
        export_name = "./randomcut_"+date_time+collection+".mp4"
        if self.verbose>1:
            print("export to:", export_name, movie_total)
        try:
            f = open(Path(export_name).with_suffix('.srt'),"w+")
            f.write(subtitle)
            f.close()
        except Exception as e:
            if self.verbose>0:
                print("subtitle failed:",e)
        final_video = mp.concatenate_videoclips(clips)
        final_video.write_videofile(export_name, 
                                    fps = self.movie_fps,
                                    codec='libx264')
        return export_name

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by mlaiacker on %s.
  Copyright 2020 mlaiacker. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-r", "--recursive", dest="recurse", action="store_true", help="recurse into subfolders [default: %(default)s]")
        parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]", default = 0)
        parser.add_argument("-i", "--include", dest="include", help="only include paths matching this regex pattern. Note: exclude is given preference over include. [default: %(default)s]", metavar="RE" )
        parser.add_argument("-e", "--exclude", dest="exclude", help="exclude paths matching this regex pattern. [default: %(default)s]", metavar="RE" )
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument('-d', '--dir', help="directory to find clips in [default: %(default)s]", default=".", type=str, metavar="path")
        parser.add_argument('-n', '--num', help="max number of clips to use", default=300, type=int)
        parser.add_argument('-l', '--length', help="length of each clip[default: %(default)s]", default =5, type=int)
        parser.add_argument('-x', '--rand', help="random file name order", action="store_true")
        parser.add_argument(dest="paths", help="patterns of files to include [default: %(default)s]", nargs='+', default="*.mp4", metavar="pattern")

        # Process arguments
        args = parser.parse_args()

        paths = args.paths
        verbose = args.verbose
        recurse = args.recurse
        inpat = args.include
        expat = args.exclude

        if verbose > 0:
            print("Verbose mode on")
            if recurse:
                print("Recursive mode on")
            else:
                print("Recursive mode off")

        if inpat and expat and inpat == expat:
            raise CLIError("include and exclude pattern are equal! Nothing will be processed.")
        
        randomcut = RandomCut()
        randomcut.verbose = verbose
        randomcut.movie_random = args.rand
        randomcut.setClipLength(args.length)
        randomcut.setDir(args.dir)
        randomcut.setMaxClips(args.num)

        for inpath in paths:
            ### do something with inpath ###
            #print(inpath)
            randomcut.addPattern(inpath)

        randomcut.findClips()
        randomcut.cut()
                    
        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
'''    except Exception as e:
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2'''

if __name__ == "__main__":
    #if DEBUG:
        #sys.argv.append("-h")
        #sys.argv.append("-v")
        #sys.argv.append("-r")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'randomcut_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())