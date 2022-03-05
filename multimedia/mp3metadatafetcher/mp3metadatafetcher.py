import eyed3
import os
import fnmatch
import json
import os
import sys
import itunespy
import requests
import musicbrainzngs
import re
import urllib.parse
import time
import string
import unidecode

from PIL import Image
from shutil import copyfile
from get_cover_art import CoverFinder

FOLDERSOURCE              = "/mp3metadatafetcher/media"
FOLDERDESTINATION         = "/mp3metadatafetcher/converted"
GETMUSICBRAINZCOVERIMAGES = True
DELETESOURCEFILES         = True
COVERRELEASEID_FILEPREFIX_MB = "musicbrainz-cover-releaseid-"
METADATA_FOLDER           = FOLDERSOURCE + "/metadata"

MB_USERAGGENT_NAME    = "Rui's new app"
MB_USERAGGENT_VERSION = "0.4"
MB_USERAGGENT_LINK    = "https://ourNewMusikApp.de"


def saveAudioFile(audiofile):
    #audiofile.tag.save(version=(1,None,None))
    audiofile.tag.save()
    #audiofile.tag.save(version=(2,3,0))

#################################################################
def initializeMp3File(mp3File):

    resetMetadata = False
    initString = "[INIT]"
    if (initString in mp3File):
        resetMetadata = True
        filenameOnly = os.path.basename(mp3File)
        pathOnly = os.path.dirname(mp3File)
        newFileName = pathOnly + "/" + filenameOnly[len(initString):]
        os.rename(mp3File, newFileName)
        mp3File = newFileName

    try:
        audiofile = eyed3.load(mp3File)
        if (audiofile.tag == None):
            audiofile.initTag()
            saveAudioFile(audiofile)
        # else:
        #     title = audiofile.tag.title
        #     temp = title.strip("-")
        #     if (len(temp) > 1):
        #         audiofile.tag.title = None
        filenameOnly = os.path.basename(mp3File)
        if resetMetadata == True:
            audiofile.tag.artist = None
            audiofile.tag.title = None
            saveAudioFile(audiofile)

    except Exception as e:
        print ("- initializeMp3File: EXCEPTION " + str(e))
        audiofile = None
    return audiofile

#################################################################
def writeTempFileData(filename,data):
    file = open(filename, 'wb')
    file.write(data)
    file.close()
#################################################################
def readTempFileData(filename):
    file = open(filename, 'rb')
    data = file.read()
    file.close()
    return data
#################################################################
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

#################################################################
def specialCleanUpForArtist(artist,splitText):

    tempStr = artist.split(splitText)
    if (len(tempStr) > 1):
        artist = tempStr[0]
    artist = cleanUpText(artist)
    artist =  artist.strip()
    return artist
#################################################################
def cleanupFilenameForSearch(filename):

    filenameOnly = os.path.basename(filename)
    filenameBase = os.path.splitext(filenameOnly)[0]
    filenameBase = filenameBase.replace("_","-")

    text = cleanUpText(filenameBase)

    #text = specialCleanUpForArtist(text,",")
    #text = specialCleanUpForArtist(text,"&")

    return text
#################################################################
def cleanUpFilename(filename):
    filename = re.sub("([\(\[]).*?([\)\]])", "\g<1>\g<2>",filename)
    filename = filename.replace("()","")
    filename = filename.replace("[]","")
    filename = filename.replace("'","")
    filename = filename.replace("–","-")
    filename, file_extension = os.path.splitext(filename)    
    filename = filename.strip() + file_extension
    return filename

#################################################################
def normalizeArtistAndTitle(filename, artist, title):
    if (title == None or artist == None):

        filenameOnly = os.path.basename(filename)
        filenameBase = os.path.splitext(filenameOnly)[0]
        filenameBase = filenameBase.replace("_","-")

        artistFilename= None    
        titleFilename = None
        info = filenameBase.split("-") 


        if (len(info) > 1):
            artistFilename = info[0]
            titleFilename  = info[1]

            if (artistFilename != None):
                #artist = specialCleanUpForArtist(artistFilename,",")
                artist = specialCleanUpForArtist(artistFilename,"&")
            if (titleFilename  != None):
                title = titleFilename
    
    if (title  != None):
        title  = cleanUpText(title)
    if (artist != None):
        artist = specialCleanUpForArtist(artist,",")

    return (artist, title)

#################################################################
def cleanupAudiofileArtistTitle(audiofile):

    artist = audiofile.tag.artist
    title = audiofile.tag.title

    if (artist != None):
        artist = specialCleanUpForArtist(artist,",")
        artist = specialCleanUpForArtist(artist,"&")
    
    if (title  != None):
        title  = cleanUpText(title)
    audiofile.tag.artist = artist
    audiofile.tag.title = title
    saveAudioFile(audiofile)

    artistTemp = artist.split("-")
    if (len(artistTemp) > 1):
        artist = artistTemp[0]

    return audiofile


#################################################################
def updatedMetadataThroughFilename(mp3Filename):

    audiofile = initializeMp3File(mp3Filename)

    artist = None
    title = None
    
    (artist,title) =  normalizeArtistAndTitle(mp3Filename, artist,title)

    #print ("- updateMetadataWithYoutubeInfo: artist = " + str(artist))
    #print ("- updateMetadataWithYoutubeInfo: title  = " + str(title))

    if (audiofile != None):

        #artist = audiofile.tag.artist
        #title  = audiofile.tag.title

        if (artist != None and title != None):
            try:
                audiofile.tag.artist = artist
                audiofile.tag.title = title
                saveAudioFile(audiofile)
                #if (GETMUSICBRAINZCOVERIMAGES == True):
                #    audiofile = addCoverImage(mp3Filename, audiofile, artist,title)
            except Exception as e:
                print (" - updatedMetadataWithYoutubeInfo: EXCEPTION " + str(e))

    return audiofile


#################################################################
def writeItunesResponseToAudiofile(audiofile, thisResponse):
    #tempFile = FOLDERSOURCE + "/temp.jpg"
    try:
        artist = thisResponse['artistName']
        title  = thisResponse['trackName']

        audiofile.tag.artist = artist
        audiofile.tag.title  = title
        if ('collectionName' in thisResponse):
            audiofile.tag.album = thisResponse['collectionName'] 

        if ('trackNumber' in thisResponse):
            audiofile.tag.track = thisResponse['trackNumber'] 

        if ('trackCount' in thisResponse):
            audiofile.tag.track_total = thisResponse['trackCount'] 

        if ('discCount' in thisResponse):
            audiofile.tag.disc = thisResponse['discCount'] 

        if ('releaseDate' in thisResponse):
            audiofile.tag.releaseDate = thisResponse['releaseDate']
        if ('artistViewUrl' in thisResponse):
            audiofile.tag.artistViewUrl = thisResponse['artistViewUrl']

        if ('collectionViewUrl' in thisResponse):
            audiofile.tag.collectionViewUrl = thisResponse['collectionViewUrl']

        if ('trackTimeMillis' in thisResponse):
            audiofile.tag.trackTimeMillis = thisResponse['trackTimeMillis']

        ##TBD: find out how to include lyrics into the mp3
        ##audiofile.tag.lyrics.set(u"""la la la""")

        if ('primaryGenreName' in thisResponse):
            audiofile.tag.primaryGenreName= thisResponse['primaryGenreName']
            audiofile.tag.genre = thisResponse['primaryGenreName']

        urlFromAPI = thisResponse['artworkUrl100']
        url        = urlFromAPI.replace("/source/100x100bb.jpg","/source/1000x1000bb.jpg")

        data = requests.get(url, stream=True).raw.data
        audiofile.tag.images.set(3, data, 'image/jpg')
        audiofile.tag.images.set(1, data, 'image/jpg')
        saveAudioFile(audiofile)
        print ("- addItunesCoverArt: Added cover art from iTunes")
    except Exception as e:
        print ("- writeItunesResponseToAudiofile: EXCEPTION " + str(e))

    return audiofile
#################################################################
def checkIfFoundMatch(foundArtist, foundTitle, artist, title):

    if (artist != None):
        artist = artist.lower()
        artist = artist.strip()
    else:
        return False
    if (title != None):
        title = title.lower()
        title = title.strip()
    else:
        return False
    if (foundArtist != None):
        foundArtist = foundArtist.lower()
        foundArtist = foundArtist.strip()
    else:
        return False
    if (foundTitle != None):
        foundTitle = foundTitle.lower()
        foundTitle = foundTitle.strip()
    else:
        return False

    if (artist == foundArtist and title == foundTitle):
        return True

#################################################################
def getMetadataFile(mp3Filename, extension):
    filenameBase = os.path.splitext(mp3Filename)[0]
    extensionFilename = filenameBase + extension
    if (os.path.isfile(extensionFilename) == True):
        return extensionFilename
    return None
#################################################################
def addCoverImageForReleaseId(mp3Filename, audiofile, releaseId):
    musicbrainzngs.set_useragent(MB_USERAGGENT_NAME, MB_USERAGGENT_VERSION, MB_USERAGGENT_LINK)
    try:
        ## If no iTunes success, try musicbrainz
        data = musicbrainzngs.get_image_front(releaseId, size=1)
        audiofile.tag.images.set(3, data, 'image/jpg')
        audiofile.tag.images.set(1, data, 'image/jpg')
        audiofile.tag.comments.set("{'Musicbrainz-releaseID' : '" + str(releaseId) +"'}")
        saveAudioFile(audiofile)
        return audiofile
    except Exception as e:
        print (" - addCoverImageForReleaseId: EXCEPTION found")
        print ("   >> " + str(e))

    return audiofile

#################################################################
def addCoverImage(mp3Filename, audiofile, myArtist,myTitle):
    musicbrainzngs.set_useragent(MB_USERAGGENT_NAME, MB_USERAGGENT_VERSION, MB_USERAGGENT_LINK)
    #results = musicbrainzngs.search_artists(artist=myArtist)

    #print ("- addCoverImage: Searching for >" + myArtist + " - " + myTitle + "<")
    results = musicbrainzngs.search_release_groups(myArtist + " " + myTitle, limit=25)
    
    if (len(results) > 0):
        #print ("- addCoverImage: Found " + str(len(results)) + " results")
        artist = None
        title = None
        releaseId = None
        for release_group in results["release-group-list"]:
            if (len(release_group["artist-credit"]) > 0):
                artist     = release_group["artist-credit"][0]["name"]
            if (len(release_group["release-list"]) > 0):
                title      = release_group["release-list"][0]["title"]
                releaseId  = release_group["release-list"][0]["id"]
                (artist,title) =  normalizeArtistAndTitle(mp3Filename, artist,title)
            #print ("- addCoverImage: found artist    " + artist)
            #print ("- addCoverImage: found title     " + title)

            # check for exact match first
            if (checkIfFoundMatch(artist, title, myArtist, myTitle) == True):
                print ("- addCoverImage: found matching releaseId for artist >" + artist +"<, >" + title + "<: " + releaseId)
                audiofile = addCoverImageForReleaseId(mp3Filename, audiofile, releaseId)
                return audiofile
    # ## if no cover image was foudn through musicbrainz, try itunes instead
    # if len( audiofile.tag.images ) == 0:
    #     audiofile = addItunesCoverArt(audiofile,None)

    return audiofile

#################################################################
def moveFile(audiofile, sourceFile):

    #audiofile = cleanupAudiofileArtistTitle(audiofile)
    artist = audiofile.tag.artist
    title = audiofile.tag.title

    if (artist == None):
        audiofile = updatedMetadataThroughFilename(sourceFile)
        artist = audiofile.tag.artist
        title = audiofile.tag.title

    if len( audiofile.tag.images ) == 0:
        audiofile = addCoverImage(sourceFile, audiofile, artist,title)
    
    filenameOnly = os.path.basename(sourceFile)
    filenameBase = os.path.splitext(filenameOnly)[0]
    textWithoutBrackets = re.sub("[\(\[].*?[\)\]]", "", filenameBase).strip()

    if (artist != None):
        folderDestinationNew = FOLDERDESTINATION + "/" + artist.title() + "/"
        if (title != None):
            newFilename = folderDestinationNew + artist + " - " + title + ".mp3"
        else:
            newFilename = folderDestinationNew + artist + " - " + textWithoutBrackets + ".mp3"
    else:

        folderDestinationNew = FOLDERDESTINATION + "/unknown artists/"
        if (title != None):
            newFilename = folderDestinationNew  + title + ".mp3"
        else:
            newFilename = folderDestinationNew  + textWithoutBrackets + ".mp3"
    #print (" - moveFile: Old filename  >" + sourceFile + "<")
    #print (" - moveFile: New filename  >" + newFilename + "<")
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

#################################################################
def checkIfGoodResult(searchString, thisResponse):
    result = False

    artist = thisResponse['artistName']
    title  = thisResponse['trackName']

    #artist = specialCleanUpForArtist(artist,",")
    # artist = specialCleanUpForArtist(artist,"&")
    # artist = cleanUpText(artist)
    # title = cleanUpText(title)

    #normalize the search, artist and title to get better results
    #pattern = re.compile('\W')
        #text = unidecode.unidecode(text)

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

#################################################################
def addItunesCoverArt(audiofile):

    mp3File= audiofile.path

    filenameOnly = os.path.basename(mp3File)
    filenameBase = os.path.splitext(filenameOnly)[0]

    searchString = cleanupFilenameForSearch(filenameBase)

    req_string = 'https://itunes.apple.com/search?term=' + searchString + '&entity=musicTrack&limit=10'

    try:
        # Adding 3 seconds of delay here to not exceed iTunes API access limits of 20 API calls per minute
        # Checkout https://developer.apple.com/forums/thread/66399?page=2 for some more information
        time.sleep(3)
        response = requests.get(req_string)
        #print ("- addItunesCoverArt: response statue code  >" + str(response.status_code) + "< for " + req_string)

        if response.status_code == 200:
            response = response.json()
            for thisResponse in response['results']:
                goodResult = checkIfGoodResult(searchString, thisResponse)
                if (goodResult == True):
                    audiofile = writeItunesResponseToAudiofile(audiofile, thisResponse)
                    return audiofile
    except Exception as e:
        print (" - addItunesCoverArt: EXCEPTION found")
        print ("   >> request: " + req_string)
        print ("   >> " + str(e))
        return audiofile

    return audiofile
#################################################################
def getMetadata(audiofile):

    try:
        audiofile = addItunesCoverArt(audiofile)
    except Exception as e:
        print ("- moveFile: EXCEPTION " + str(e))
        audiofile = None
    
    return audiofile


#################################################################
def createCopyOfOriginalFile(orig):
    filenameOnly = os.path.basename(orig)
    filenameOnly = cleanUpFilename(filenameOnly)
    newFile = METADATA_FOLDER + "/" + filenameOnly
    #print ("DEBUG " + orig)
    #print ("DEBUG " + newFile)
    fileExists = os.path.isfile(newFile)
    if (fileExists == True):
        os.remove(newFile)
    if not os.path.exists(METADATA_FOLDER):
        os.makedirs(METADATA_FOLDER)

    copyfile(orig, newFile)
    return  newFile

def cleanUpFolders():

    command = "find " + FOLDERSOURCE + " -name '.DS_Store' -delete"
    os.system(command)
    command = "find " + FOLDERSOURCE + " -type d -empty -delete"
    os.system(command)

#################################################################
#################################################################
cleanUpFolders()

for folder, dirs, files in os.walk(FOLDERSOURCE):
    for filename in files:
        if fnmatch.fnmatch(filename, "*.mp3"):
            mp3filenameFullpath = folder + "/" + filename
            print ("################################")
            print (mp3filenameFullpath)

            newFile = createCopyOfOriginalFile(mp3filenameFullpath)

            audiofile = initializeMp3File(newFile)
            audiofile = getMetadata(audiofile)

            if audiofile != None:
                newFile = audiofile.path
                moveFile(audiofile,newFile)
                if (DELETESOURCEFILES == True):
                    os.remove(mp3filenameFullpath)
cleanUpFolders()
