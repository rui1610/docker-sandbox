import os
import time
import requests
import musicbrainzngs

from helperGeneric import checkIfGoodResult

MB_USERAGGENT_NAME    = "Rui's new app"
MB_USERAGGENT_VERSION = "0.4"
MB_USERAGGENT_LINK    = "https://ourNewMusikApp.de"


def getMetadataFromMusicbrainzngs(searchString):

    maximumResults = 10
    musicbrainzngs.set_useragent(MB_USERAGGENT_NAME, MB_USERAGGENT_VERSION, MB_USERAGGENT_LINK)

    response = musicbrainzngs.search_release_groups(searchString, limit=maximumResults)

    try:
        result = []

        for thisResponse in response['release-group-list']:
            artist     = thisResponse["artist-credit"][0]["name"]
            title      = thisResponse["release-list"][0]["title"]
            releaseId  = thisResponse["release-list"][0]["id"]
            fitScore   = thisResponse["ext:score"]
            goodResult = checkIfGoodResult(searchString, artist, title)
            if (goodResult == True and len(result) < 5):
                thisResponse["releaseId"] = releaseId
                if fitScore is not None and int(fitScore) > 90:
                    result.append(thisResponse)

        return result

    except Exception as e:
        print (" - addItunesCoverArt: EXCEPTION found")
        print ("   >> search string: " + searchString)
        print ("   >> " + str(e))
        return None

    return None
