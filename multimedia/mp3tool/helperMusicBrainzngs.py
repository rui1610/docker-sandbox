import os
import time
import requests
import musicbrainzngs
from helperEyed3 import getImageDescriptionForType, getMusicbrainzCover, saveAudioFile

from helperGeneric import checkIfGoodResult

MB_USERAGGENT_NAME    = "Rui's new app"
MB_USERAGGENT_VERSION = "0.4"
MB_USERAGGENT_LINK    = "https://ourNewMusikApp.de"

def getMetadataFromMusicbrainzngs(searchString):

    try:
        response = sendRequestToMusicbrainz(searchString)
        result = []

        for thisResponse in response['recording-list']:
            artist     = thisResponse["artist-credit-phrase"]
            title      = thisResponse["title"]
            fitScore   = thisResponse["ext:score"]
            goodResult = checkIfGoodResult(searchString, artist, title)
            if (goodResult == True and len(result) < 5):
                if fitScore is not None and int(fitScore) > 90:
                    result.append(thisResponse)
        return result

    except Exception as e:
        print (" - addItunesCoverArt: EXCEPTION found")
        print ("   >> search string: " + searchString)
        print ("   >> " + str(e))
        return None

    return None

def sendRequestToMusicbrainz(searchString):

    maximumResults = 50
    musicbrainzngs.set_useragent(MB_USERAGGENT_NAME, MB_USERAGGENT_VERSION, MB_USERAGGENT_LINK)

    response = musicbrainzngs.search_recordings(searchString, limit=maximumResults)

    return response

def addMetadataFromMusicbrainzngs(audiofile):

    searchString = audiofile.tag.artist + " - " + audiofile.tag.title

    myData = getMetadataFromMusicbrainzngs(searchString)
    if myData is not None and len(myData) > 0:
        thisResponse = myData[0]

        audiofile.tag.artist = thisResponse["artist-credit-phrase"]
        audiofile.tag.title  = thisResponse["title"]

        releaseId = None

        if ('release-list' in thisResponse and len(thisResponse["release-list"]) > 0):
            audiofile.tag.album = thisResponse["release-list"][0]["title"]

            if ('date' in thisResponse["release-list"][0]):
                audiofile.tag.releaseDate = thisResponse["release-list"][0]["date"]
            if ('id' in thisResponse["release-list"][0]):
                releaseId = thisResponse["release-list"][0]["id"]
                cover = getMusicbrainzCover(releaseId,"cover")
                if cover is not None:
                    imageType = 3
                    audiofile.tag.images.set(imageType, cover, 'image/jpg', getImageDescriptionForType(imageType))            
                cover = getMusicbrainzCover(releaseId,"icon")
                if cover is not None:
                    imageType = 1
                    audiofile.tag.images.set(imageType, cover, 'image/jpg', getImageDescriptionForType(imageType))            

            if ('medium-list' in thisResponse["release-list"][0]):
                if len(thisResponse["release-list"][0]["medium-list"]) > 0:
                    entryMediumList = thisResponse["release-list"][0]["medium-list"]
                    if 'track-list' in entryMediumList[0] and len(entryMediumList[0]["track-list"]) > 0:
                        if "number" in entryMediumList[0]["track-list"][0]:
                            audiofile.tag.track = entryMediumList[0]["track-list"][0]["number"]
                        if "length" in entryMediumList[0]["track-list"][0]:
                            audiofile.tag.trackTimeMillis = entryMediumList[0]["track-list"][0]["length"]

            if ('medium-track-count' in thisResponse["release-list"][0]):
                audiofile.tag.track_total = thisResponse["release-list"][0]["medium-track-count"] 

            if ('medium-count' in thisResponse["release-list"][0]):
                audiofile.tag.disc = thisResponse["release-list"][0]["medium-count"] 

        if ('tag-list' in thisResponse):
            tags = thisResponse["tag-list"]
            primaryGenre = None
            maxCounter = 0
            for tag in tags:
                count = int(tag["count"])
                name = tag["name"]
                if count > maxCounter:
                    primaryGenre = name
            if primaryGenre is not None:
                audiofile.tag.primaryGenreName= primaryGenre
                audiofile.tag.genre = primaryGenre    
        saveAudioFile(audiofile)  
      