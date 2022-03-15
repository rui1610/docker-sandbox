import os
import time
import requests

from helperGeneric import checkIfGoodResult

def getMetadataFromItunes(searchString):

    maximumResults = 10
    searchString = searchString.replace(':', '/')


    req_string = 'https://itunes.apple.com/search?term=' + searchString + '&entity=musicTrack&limit=' + str(maximumResults)

    try:
        # Adding 3 seconds of delay here to not exceed iTunes API access limits of 20 API calls per minute
        # Checkout https://developer.apple.com/forums/thread/66399?page=2 for some more information
        time.sleep(3)
        response = requests.get(req_string)
        result = []
        if response.status_code == 200:
            response = response.json()
            for thisResponse in response['results']:
                artist = thisResponse['artistName']
                title = thisResponse['trackName']
                goodResult = checkIfGoodResult(searchString, artist, title)
                if (goodResult == True and len(result) < 5):
                    result.append(thisResponse)
        return result

    except Exception as e:
        print (" - addItunesCoverArt: EXCEPTION found")
        print ("   >> request: " + req_string)
        print ("   >> " + str(e))
        return None

    return None


