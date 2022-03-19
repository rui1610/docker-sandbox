import inotify.adapters
import os
from mp3metadatafetcher import addMetadataToFiles
i = inotify.adapters.InotifyTree('media')

for event in i.event_gen(yield_nones=False):
  (_, type_names, path, filename) = event

  for event_type in type_names:
    if event_type == "IN_CREATE": 
      filenameOnly = os.path.basename(filename)
      filenameBase = os.path.splitext(filenameOnly)[0]
      if (filenameBase == "mp3"):
        addMetadataToFiles()

