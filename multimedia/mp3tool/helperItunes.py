from email.mime import audio
import time
import requests
import urllib.parse
from helperEyed3 import getITunesCoverBig, getITunesCoverSmall, getImageDescriptionForType, saveAudioFile

from helperGeneric import fuzzyCheckIfGoodResult, determineArtistAndTitleFromFilename


def sendRequestToItunes(searchString):

    maximumResults = 200
    searchString = searchString.replace(':', '/')

    term = {"term":searchString}

    termUrlEncoded = urllib.parse.urlencode(term)
    req_string = 'https://itunes.apple.com/search?' + termUrlEncoded + '&entity=musicTrack&type=songs&limit=' + str(maximumResults)

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


def getMetadataFromItunes(audiofile):
    result = None
    matches = []

    artist = audiofile.tag.artist
    title = audiofile.tag.title

    response = sendRequestToItunes(artist + " " + title)

    if response is not None and "results" in response:
        for thisResponse in response['results']:
            artistFound = thisResponse['artistName']
            titleFound = thisResponse['trackName']
            matchRatio = fuzzyCheckIfGoodResult(artist, title, artistFound, titleFound)
            if matchRatio > 90:
                thisResponse["matchRatio"] = matchRatio
                matches.append(thisResponse)
    
    if len(matches) == 0:
        [artistFilename, titleFilename] = determineArtistAndTitleFromFilename(audiofile.path)
        if artistFilename != artist or titleFilename != title:
            response = sendRequestToItunes(artistFilename + " " + titleFilename)

            if response is not None and "matches" in response:
                for thisResponse in response['results']:
                    artistFound = thisResponse['artistName']
                    titleFound = thisResponse['trackName']
                    matchRatio = fuzzyCheckIfGoodResult(artist, title, artistFound, titleFound)
                    if matchRatio > 90:
                        thisResponse["matchRatio"] = matchRatio
                        matches.append(thisResponse)

    result = getBestMatch(audiofile,matches)

    return result

def getBestMatch(audiofile, response):

    artist = audiofile.tag.artist
    title = audiofile.tag.title

    result = None

    maxMatch = 0
    for entry in response:
        thisArtist = entry["artistName"]
        thisTitle  = entry["trackName"]
        match  = entry["matchRatio"]
        if match > maxMatch:
            maxMatch = match
            result = entry
    return result    


def addMetadataFromItunes(audiofile):

#    searchString = audiofile.tag.artist + " " + audiofile.tag.title

    thisResponse = getMetadataFromItunes(audiofile)
    if thisResponse is not None:

        audiofile.tag.artist = thisResponse["artistName"]
        audiofile.tag.title  = thisResponse["trackName"]

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

        if ('primaryGenreName' in thisResponse):
            audiofile.tag.primaryGenreName= thisResponse['primaryGenreName']
            audiofile.tag.genre = thisResponse['primaryGenreName']        
        
        #comment = {"itunes-trackid" :  thisResponse['trackId'],"itunes-collectionid": thisResponse['collectionId'],"itunes-previewurl":thisResponse['previewUrl']}
        #thisComment = str(dictToString(comment).encode("utf-8"))
        audiofile.tag.comments.set("")

        cover = getITunesCoverBig(thisResponse)
        icon = getITunesCoverSmall(thisResponse)
        # https://eyed3.readthedocs.io/en/latest/eyed3.id3.html#eyed3.id3.frames.ImageFrame
        #audiofile.tag.images.set(0, cover, 'image/jpg', u"othercover")
        imageType = 3
        audiofile.tag.images.set(imageType, cover, 'image/jpg', getImageDescriptionForType(imageType))            
        imageType = 1
        audiofile.tag.images.set(imageType, icon, 'image/jpg', getImageDescriptionForType(imageType))            
        #audiofile.tag.images.set(2, icon, 'image/jpg', u"othericon")            
        
        saveAudioFile(audiofile)
