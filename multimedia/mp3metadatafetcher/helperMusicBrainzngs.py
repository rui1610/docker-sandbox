import os
import time
import requests
import musicbrainzngs

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
