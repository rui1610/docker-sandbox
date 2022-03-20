import inotify.adapters
import os
from mp3metadatafetcher import addMetadataToFiles
from pathlib import Path 

WATCHFOLDER = "media"

def splitFileName(file):
    dir = os.path.dirname(os.path.realpath(file))
    name = Path(file).name
    prefix, suffix = name.split(".")
    return dir,name,prefix,suffix

i = inotify.adapters.InotifyTree(WATCHFOLDER)

for event in i.event_gen(yield_nones=False):
  (_, type_names, path, filename) = event

  for event_type in type_names:
    #print("PATH=[{}] FILENAME=[{}] EVENT_TYPES={}".format( path, filename, type_names))    
    dir,name,prefix,suffix = splitFileName(filename)
    if event_type == "IN_CLOSE_WRITE": 
      if (suffix == "mp3"):
        print("detected new file " + name + " in folder " + WATCHFOLDER)
        addMetadataToFiles()

