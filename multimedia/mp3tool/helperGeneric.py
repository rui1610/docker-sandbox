from email.mime import audio
import os
import re
from helperJson import getJsonFromFile
import unittest
import unidecode
from shutil import copyfile

from helperEyed3 import getAudioFile
DELETESOURCEFILES = True
FOLDERDESTINATION = "/mp3tool/output"
SEPERATOR = " - "


def determineArtistAndTitleFromFilename(filename):
    artist = None
    title = None

    filenameOnly = os.path.basename(filename)
    filenameBase = os.path.splitext(filenameOnly)[0]
    text = filenameBase
    counterSeperator = text.count(SEPERATOR)
    if counterSeperator == 1:
        artist, title = text.split(SEPERATOR)
    if counterSeperator > 1:
        posLastSeparator = text.rindex(SEPERATOR)
        artist = text[posLastSeparator:]
        title = text[:posLastSeparator+len(SEPERATOR)]
    
    # Remove all text in brackets
    title = re.sub("[\(\[].*?[\)\]]", "", title).strip()
    artist = re.sub("[\(\[].*?[\)\]]", "", artist).strip()

    # Remove all text that has things like "feat."
    deletionList = ["feat."]
    for entry in deletionList:
        if entry in artist:
            pos = artist.rindex(entry)
            artist = artist[:pos]

    return [artist, title]

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
def cleanupFilenameForSearch(audiofile, filename):

    filenameOnly = os.path.basename(filename)
    filenameBase = os.path.splitext(filenameOnly)[0]
    text = filenameBase.replace("_","-")

    text = filenameBase.replace("[INIT]","")
    #text = cleanUpText(filenameBase)

    text = specialCleanUpForArtist(text,",")
    #text = specialCleanUpForArtist(text,"&")

    if " - " not in text:
        artist = audiofile.tag.artist
        title = audiofile.tag.title
        if artist is not None and title is not None:
            text = artist + " - " + title
        if artist is not None and title is None:
            text = artist + " - " + text

    return text

def deriveArtistAndTitleFromSearchString(audiofile, searchString):
    if " - " in searchString and audiofile is not None:
        artist, title = searchString.split(" - ")
        audiofile.tag.artist = artist
        audiofile.tag.title = title
    
    return audiofile

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

def metadataMissing(audiofile):
    result = True

    if hasCover(audiofile) and hasArtist(audiofile) and hasTitle(audiofile) and hasLyrics(audiofile):
        result = False

    return result

def hasArtist(audiofile):
    hasInfo = False
    if audiofile is not None:

        info = audiofile.tag.artist
        if info is not None or info != "":
            hasInfo = True
    return hasInfo

def hasCover(audiofile):
    hasInfo = False
    if audiofile is not None:
        counter = len(audiofile.tag.images )
        if counter > 0:
            hasInfo = True
    return hasInfo

def hasTitle(audiofile):
    hasInfo = False
    if audiofile is not None:
        info = audiofile.tag.title
        if info is not None or info != "":
            hasInfo = True
    return hasInfo

def hasLyrics(audiofile):
    hasLyrics = False
    if audiofile is not None:
        for lyric in audiofile.tag.lyrics:
            text = lyric.text
            if text is not None and len(text) > 0:
                hasLyrics = True
    return hasLyrics

#################################################################
def moveFile(audiofile, sourceFile):

    #audiofile = cleanupAudiofileArtistTitle(audiofile)
    artist = audiofile.tag.artist
    title = audiofile.tag.title
    counterImages = len(audiofile.tag.images )

    filenameOnly = os.path.basename(sourceFile)
    filenameBase = os.path.splitext(filenameOnly)[0]

    if artist is not None:
        artist = artist.strip()
    if title is not None:
        title = title.strip()
    else:
        title = filenameBase

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
            print ("- moveFile: moved file to " + newFilename)
    except Exception as e:
        print ("- moveFile: EXCEPTION " + str(e))
        audiofile = None
    
    return None

