import os
import fnmatch
import os
from helperEyed3 import getAudioFile, getJsonFromComment, updateMp3WithMetadata
from helperGeneric import cleanupFilenameForSearch, mp3ToBeUpdated
from helperItunes import getMetadataFromItunes
from helperJson import addKeyValuePair, saveJsonToFile


from shutil import copyfile

from helperMusicBrainzngs import getMetadataFromMusicbrainzngs
from helperGeneric import moveFile

FOLDERSOURCE              = "/mp3metadatafetcher/media"
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

#################################################################

def addMetadataToFile(mp3filenameFullpath):

    toBeUpdated = mp3ToBeUpdated(mp3filenameFullpath)
    if toBeUpdated == True:
        thisFile = {"file":mp3filenameFullpath}
        print("- " + mp3filenameFullpath)
        searchString = cleanupFilenameForSearch(mp3filenameFullpath)
        if "metadataitunes" not in thisFile or thisFile["metadataitunes"] is None:
            thisResult = getMetadataFromItunes(searchString)
            addKeyValuePair(thisFile,"metadataitunes", thisResult)
        if "metadatamusicbrainzngs" not in thisFile or thisFile["metadatamusicbrainzngs"] is None:
            thisResult = getMetadataFromMusicbrainzngs(searchString)
            addKeyValuePair(thisFile,"metadatamusicbrainzngs", thisResult)
        audiofile = getAudioFile(mp3filenameFullpath)
        updateMp3WithMetadata(audiofile,thisFile)
        moveFile(audiofile,mp3filenameFullpath)
    else:
        audiofile = getAudioFile(mp3filenameFullpath)
        moveFile(audiofile,mp3filenameFullpath)


def addMetadataToFiles():
    allFiles=[]
    for folder, dirs, files in os.walk(FOLDERSOURCE):
        for filename in files:
            if fnmatch.fnmatch(filename, "*.mp3"):
                mp3filenameFullpath = folder + "/" + filename
                #print(mp3filenameFullpath)
                toBeUpdated = mp3ToBeUpdated(mp3filenameFullpath)
                if toBeUpdated == True:
                    thisFile = {"file":mp3filenameFullpath}
                    allFiles.append(thisFile)

    for file in allFiles:
        filename = file["file"]
        print("- " + filename)
        searchString = cleanupFilenameForSearch(filename)
        if "metadataitunes" not in file or file["metadataitunes"] is None:
            thisResult = getMetadataFromItunes(searchString)
            addKeyValuePair(file,"metadataitunes", thisResult)
        if "metadatamusicbrainzngs" not in file or file["metadatamusicbrainzngs"] is None:
            thisResult = getMetadataFromMusicbrainzngs(searchString)
            addKeyValuePair(file,"metadatamusicbrainzngs", thisResult)
        audiofile = getAudioFile(filename)
        updateMp3WithMetadata(audiofile,file)
        moveFile(audiofile,filename)

    cleanUpFolders()
