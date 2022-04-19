import os
import fnmatch
import os
from helperEyed3 import getAudioFile
from helperGeneric import cleanupFilenameForSearch, metadataMissing
from helperItunes import addMetadataFromItunes
from helperLyrics import addMetadataFromGenius
from helperMusicBrainzngs import addMetadataFromMusicbrainzngs

from helperGeneric import moveFile
from helperEyed3 import addNameToImageIfMissing

FOLDERSOURCE              = "/mp3tool/input"
GETMUSICBRAINZCOVERIMAGES = True
DELETESOURCEFILES         = True
COVERRELEASEID_FILEPREFIX_MB = "musicbrainz-cover-releaseid-"
METADATA_FOLDER           = FOLDERSOURCE + "/metadata"

def cleanUpFolders():

    command = "find " + FOLDERSOURCE + " -name '.DS_Store' -delete"
    os.system(command)
    command = "find " + FOLDERSOURCE + " -type d -empty -delete"
    os.system(command)
    command = "find " + FOLDERSOURCE + " -name '*.webp' -delete"
    os.system(command)
    command = "find " + FOLDERSOURCE + " -name '*.json' -delete"
    os.system(command)
    command = "find " + FOLDERSOURCE + " -name '*.jpg' -delete"
    os.system(command)


def addMetadataToFiles():
    allFiles=[]
    for folder, dirs, files in os.walk(FOLDERSOURCE):
        for filename in files:
            if fnmatch.fnmatch(filename, "*.mp3"):
                mp3filenameFullpath = folder + "/" + filename
                print(mp3filenameFullpath)
                audiofile = getAudioFile(mp3filenameFullpath)
                searchString = cleanupFilenameForSearch(audiofile, filename)

                needsUpdate = metadataMissing(audiofile)
                if needsUpdate is True:
                    addMetadataFromGenius(audiofile)

                needsUpdate = metadataMissing(audiofile)
                if needsUpdate is True:
                    addMetadataFromItunes(audiofile, searchString)

                needsUpdate = metadataMissing(audiofile)
                if needsUpdate is True:
                    addMetadataFromMusicbrainzngs(audiofile, searchString)

                addNameToImageIfMissing(audiofile)
                moveFile(audiofile,mp3filenameFullpath)

    cleanUpFolders()

cleanUpFolders()

addMetadataToFiles()
