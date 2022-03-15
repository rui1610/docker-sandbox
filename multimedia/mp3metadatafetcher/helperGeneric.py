import os
import re
import unidecode

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

