import os
import re
import unidecode
from shutil import copyfile

from helperEyed3 import getAudioFile
DELETESOURCEFILES = True
FOLDERDESTINATION = "converted"

def cleanUpText(text):

    if (text != None):
        text = re.sub("[\(\[].*?[\)\]]", "", text).strip()

        #text = unidecode.unidecode(text)

        pattern = re.compile(r'\s+')
        text = re.sub(pattern, ' ', text)

        # text = text.strip()
        # text = text.lower()
        # text = text.title()
        # text = text.replace(',', ' ')
        text = text.replace('  ', ' ')
    return text

# #################################################################
def specialCleanUpForArtist(artist,splitText):

    tempStr = artist.split(splitText)
    if (len(tempStr) > 1):
        artist = tempStr[0]
    artist = cleanUpText(artist)
    artist =  artist.strip()
    return artist


# #################################################################
def cleanupFilenameForSearch(filename):

    filenameOnly = os.path.basename(filename)
    filenameBase = os.path.splitext(filenameOnly)[0]
    text = filenameBase.replace("_","-")

    #text = cleanUpText(filenameBase)

    text = specialCleanUpForArtist(text,",")
    text = specialCleanUpForArtist(text,"&")

    return text

#################################################################
def checkIfGoodResult(searchString, artist, title):
    result = False

    title = unidecode.unidecode(title.lower())
    artist = unidecode.unidecode(artist.lower())
    searchString = unidecode.unidecode(searchString.lower())

    artistInSearchString = False
    titleInSearchString = False

    if " - " in searchString and searchString.count(" - ") == 1:
        [myArtist,myTitle] = searchString.split(" - ")
        titleInSearchString = myTitle in title
        artistInSearchString = myArtist in artist

    else:
        artistInSearchString = artist in searchString
        titleInSearchString = title in searchString

    if (artistInSearchString == True and titleInSearchString == True):
        result = True

    return result

def mp3ToBeUpdated(mp3File):
    toBeUpdated = False
    audiofile = getAudioFile(mp3File)
    if audiofile is None:
        toBeUpdated = True
    else:
        artist = audiofile.tag.artist
        title = audiofile.tag.title
        counter = len(  audiofile.tag.images )

        if artist is None or artist == "":
            toBeUpdated = True
        
        if title is None or title == "":
            toBeUpdated = True

        if counter == 0:
            toBeUpdated = True

    return toBeUpdated


#################################################################
def moveFile(audiofile, sourceFile):

    #audiofile = cleanupAudiofileArtistTitle(audiofile)
    artist = audiofile.tag.artist
    title = audiofile.tag.title
    counterImages = len(  audiofile.tag.images )

    filenameOnly = os.path.basename(sourceFile)
    filenameBase = os.path.splitext(filenameOnly)[0]
    textWithoutBrackets = re.sub("[\(\[].*?[\)\]]", "", filenameBase).strip()

    newFilename = None
    if counterImages > 0:
        folderDestinationNew = FOLDERDESTINATION + "/ready/" + artist + "/"
        newFilename = folderDestinationNew + artist + " - " + title + ".mp3"
    else:
        folderDestinationNew = FOLDERDESTINATION + "/noCoverImageFound/"        
        newFilename = folderDestinationNew + filenameOnly


    try:
        path = os.path.dirname(newFilename)

        if not os.path.exists(path):
            os.makedirs(path)

        fileExists = os.path.isfile(newFilename) 

        if (fileExists == True):
            os.remove(newFilename)
        
        copyfile(sourceFile, newFilename)

        if (DELETESOURCEFILES == True):
            os.remove(sourceFile)
            print ("- moveFile: moved file from " + sourceFile + " to " + newFilename)
    except Exception as e:
        print ("- moveFile: EXCEPTION " + str(e))
        audiofile = None
    
    return None