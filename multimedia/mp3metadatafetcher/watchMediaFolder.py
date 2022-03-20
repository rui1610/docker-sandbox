import inotify.adapters
import os
from mp3metadatafetcher import addMetadataToFiles
i = inotify.adapters.InotifyTree('media')

for event in i.event_gen(yield_nones=False):
  (_, type_names, path, filename) = event

  for event_type in type_names:
    print("PATH=[{}] FILENAME=[{}] EVENT_TYPES={}".format( path, filename, type_names))    
    filenameOnly = os.path.basename(filename)
    filenameBase = os.path.splitext(filenameOnly)[0]
    print (filenameOnly + " - " + filenameBase )
    if event_type == "IN_CREATE": 
      if (filenameBase == "mp3"):
        addMetadataToFiles()

