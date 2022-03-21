import inotify.adapters
import os
from mp3metadatafetcher import addMetadataToFiles
from pathlib import Path 

WATCHFOLDER = "media"
EVENTSTOWAITFOR=["IN_MODIFY","IN_CLOSE_NOWRITE"]

i = inotify.adapters.InotifyTree(WATCHFOLDER)

ignoreEvents = False
for event in i.event_gen(yield_nones=False):
  (_, type_names, path, filename) = event

  if ignoreEvents == False:
    for event_type in type_names:
      print("PATH=[{}] FILENAME=[{}] EVENT_TYPES={}".format( path, filename, type_names))    
      if event_type in EVENTSTOWAITFOR and filename.endswith('.mp3') and ignoreEvents == False:
        ignoreEvents = True
        print(event_type + "> detected file event in folder " + WATCHFOLDER)
        addMetadataToFiles()
        ignoreEvents = False
        continue
