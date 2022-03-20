import inotify.adapters
import os
from mp3metadatafetcher import addMetadataToFiles
from pathlib import Path 

WATCHFOLDER = "media"

i = inotify.adapters.InotifyTree(WATCHFOLDER)

for event in i.event_gen(yield_nones=False):
  (_, type_names, path, filename) = event

  for event_type in type_names:
    #print("PATH=[{}] FILENAME=[{}] EVENT_TYPES={}".format( path, filename, type_names))    
    if event_type == "IN_CLOSE_WRITE": 
      if filename.endswith('.mp3'):
        print("detected new file " + filename + " in folder " + WATCHFOLDER)
        addMetadataToFiles()

