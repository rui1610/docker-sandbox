import os
import fnmatch
import os
import eyed3
from helperEyed3 import getAudioFile, saveAudioFile
from helperGeneric import cleanupFilenameForSearch, metadataMissing, deriveArtistAndTitleFromSearchString, determineArtistAndTitleFromFilename
from helperItunes import addMetadataFromItunes
from helperLog import initLogger
from helperLyrics import addMetadataFromGenius
from helperMusicBrainzngs import addMetadataFromMusicbrainzngs

from helperGeneric import moveFile
from helperEyed3 import addNameToImageIfMissing

import logging

log = logging.getLogger(__name__)
initLogger(logging.INFO)

FOLDERSOURCE              = "/mp3tool/input"
GETMUSICBRAINZCOVERIMAGES = True
DELETESOURCEFILES         = True
COVERRELEASEID_FILEPREFIX_MB = "musicbrainz-cover-releaseid-"
METADATA_FOLDER           = FOLDERSOURCE + "/metadata"

def cleanUpFolders():

    command = "find " + FOLDERSOURCE + " -name '.DS_Store' -delete"
    log.debug("sending this command: " + command)
    os.system(command)
    command = "find " + FOLDERSOURCE + " -type d -empty -delete"
    log.debug("sending this command: " + command)
    os.system(command)
    command = "find " + FOLDERSOURCE + " -name '*.webp' -delete"
    log.debug("sending this command: " + command)
    os.system(command)
    command = "find " + FOLDERSOURCE + " -name '*.json' -delete"
    log.debug("sending this command: " + command)
    os.system(command)
    command = "find " + FOLDERSOURCE + " -name '*.jpg' -delete"
    log.debug("sending this command: " + command)
    os.system(command)


def cleanFiles():
    allFiles=[]
    for folder, dirs, files in os.walk(FOLDERSOURCE):
        for filename in files:
            if fnmatch.fnmatch(filename, "*.mp3"):
                mp3filenameFullpath = folder + "/" + filename
                try:
                    audiofile = eyed3.load(mp3filenameFullpath) 
                    audiofile.initTag()
                    log.info("deleted tags in mp3 file " + mp3filenameFullpath)
                    saveAudioFile(audiofile)
                    log.info("Saved mp3 file " + mp3filenameFullpath)
                except Exception as e:
                    log.error("initializeMp3File: EXCEPTION " + str(e))

def addMetadataToFiles():
    allFiles=[]
    for folder, dirs, files in os.walk(FOLDERSOURCE):
        for filename in files:
            if fnmatch.fnmatch(filename, "*.mp3"):
                mp3filenameFullpath = folder + "/" + filename
                audiofile = getAudioFile(mp3filenameFullpath)

                if audiofile is not None:
                    needsUpdate = metadataMissing(audiofile)
                    if needsUpdate is True:
                        addMetadataFromItunes(audiofile)

                    needsUpdate = metadataMissing(audiofile)
                    if needsUpdate is True:
                        addMetadataFromGenius(audiofile)

                    needsUpdate = metadataMissing(audiofile)
                    if needsUpdate is True:
                        addMetadataFromMusicbrainzngs(audiofile)

                    addNameToImageIfMissing(audiofile)
                    moveFile(audiofile,mp3filenameFullpath)
                else:
                    log.warning("Could not add metadata to " + mp3filenameFullpath)

    cleanUpFolders()

cleanUpFolders()

addMetadataToFiles()
#cleanFiles()