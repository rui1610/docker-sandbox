from distutils.util import split_quoted
import time
import requests
import urllib.parse

from helperGeneric import checkIfGoodResult


def sendRequestToItunes(searchString):

    maximumResults = 50
    searchString = searchString.replace(':', '/')

    term = {"term":searchString}

    termUrlEncoded = urllib.parse.urlencode(term)
    req_string = 'https://itunes.apple.com/search?' + termUrlEncoded + '&entity=musicTrack&limit=' + str(maximumResults)

    try:
        # Adding 3 seconds of delay here to not exceed iTunes API access limits of 20 API calls per minute
        # Checkout https://developer.apple.com/forums/thread/66399?page=2 for some more information
        time.sleep(3)
        response = requests.get(req_string)
        if response.status_code == 200:
            response = response.json()
            return response
        else:
            return None

    except Exception as e:
        print (" - addItunesCoverArt: EXCEPTION found")
        print ("   >> request: " + req_string)
        print ("   >> " + str(e))
        return None


def getMetadataFromItunes(searchString):

    response = sendRequestToItunes(searchString)
    # If nothing is found try to switch artist and title
    if response == None:
        splitChars = " - "
        splitText = searchString.split(splitChars)
        if len(splitText) == 2:
            searchString = splitText[1] + splitChars + splitText[0]
            response = sendRequestToItunes(searchString)

    result = []
    for thisResponse in response['results']:
        artist = thisResponse['artistName']
        title = thisResponse['trackName']
        goodResult = checkIfGoodResult(searchString, artist, title)
        if (goodResult == True and len(result) < 5):
            result.append(thisResponse)

    return result
