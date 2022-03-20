import inotify.adapters
import os
from mp3metadatafetcher import addMetadataToFile
from pathlib import Path 

WATCHFOLDER = "media"
EVENTSTOWAITFOR=["IN_MODIFY","IN_CLOSE_NOWRITE"]

i = inotify.adapters.InotifyTree(WATCHFOLDER)

for event in i.event_gen(yield_nones=False):
  (_, type_names, path, filename) = event

  for event_type in type_names:
    print("PATH=[{}] FILENAME=[{}] EVENT_TYPES={}".format( path, filename, type_names))    
    if event_type in EVENTSTOWAITFOR and filename.endswith('.mp3'):
        print(event_type + "> detected new file " + filename + " in folder " + WATCHFOLDER)
        fullFilename = path + "/" + filename
        addMetadataToFile(fullFilename)
        continue


