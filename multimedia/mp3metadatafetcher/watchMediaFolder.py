import inotify.adapters
from mp3metadatafetcher import addMetadataToFiles
i = inotify.adapters.InotifyTree('media')

for event in i.event_gen(yield_nones=False):
  (_, type_names, path, filename) = event

  for event_type in type_names:
    if event_type == "IN_CREATE": 
        addMetadataToFiles()

