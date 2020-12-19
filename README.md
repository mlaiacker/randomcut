# randomcut
create a movie with random short clips from video files using moviepy

## usage


```
usage: randomcut.py [-h] [-r] [-v] [-i RE] [-e RE] [-V] [-d path] [-n NUM] [-l LENGTH] [-x] pattern [pattern ...]

randomcut -- create random movies from videoclips

  Created by mlaiacker on 2020-12-18.
  Copyright 2020 mlaiacker. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE

positional arguments:
  pattern               patterns of files to include [default: *.mp4]

optional arguments:
  -h, --help            show this help message and exit
  -r, --recursive       recurse into subfolders [default: False]
  -v, --verbose         set verbosity level [default: 0]
  -i RE, --include RE   only include paths matching this regex pattern. Note: exclude is given preference over include.
                        [default: None]
  -e RE, --exclude RE   exclude paths matching this regex pattern. [default: None]
  -V, --version         show program's version number and exit
  -d path, --dir path   directory to find clips in [default: .]
  -n NUM, --num NUM     max number of clips to use
  -l LENGTH, --length LENGTH
                        length of each clip[default: 5]
  -x, --rand            random file name order
```
  
