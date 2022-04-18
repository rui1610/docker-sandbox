import os
import fnmatch
import os
from helperEyed3 import getAudioFile, getJsonFromComment, updateMp3WithMetadata
from helperGeneric import cleanupFilenameForSearch, hasLyrics, mp3ToBeUpdated
from helperItunes import getMetadataFromItunes
from helperJson import addKeyValuePair, saveJsonToFile
from helperLyrics import addLyrics, deleteLyricsIfContainingHtmlTags


from shutil import copyfile

from helperMusicBrainzngs import getMetadataFromMusicbrainzngs
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
                toBeUpdated = mp3ToBeUpdated(mp3filenameFullpath)
                if toBeUpdated == True:
                    thisFile = {"file":mp3filenameFullpath}
                    allFiles.append(thisFile)
                else:
                    audiofile = getAudioFile(mp3filenameFullpath)
                    addNameToImageIfMissing(audiofile)
                    if hasLyrics(audiofile) is False:
                        addLyrics(audiofile)
                    moveFile(audiofile,mp3filenameFullpath)


    for file in allFiles:
        filename = file["file"]
        print("- " + filename)
        audiofile = getAudioFile(filename)
        if audiofile is not None:
            searchString = cleanupFilenameForSearch(audiofile, filename)
            if "metadataitunes" not in file or file["metadataitunes"] is None:
                thisResult = getMetadataFromItunes(searchString)
                addKeyValuePair(file,"metadataitunes", thisResult)
            if "metadatamusicbrainzngs" not in file or file["metadatamusicbrainzngs"] is None:
                thisResult = getMetadataFromMusicbrainzngs(searchString)
                addKeyValuePair(file,"metadatamusicbrainzngs", thisResult)
            updateMp3WithMetadata(audiofile,file)
            addLyrics(audiofile)
            #addNameToImageIfMissing(audiofile)
            moveFile(audiofile,filename)

    cleanUpFolders()

cleanUpFolders()

addMetadataToFiles()
