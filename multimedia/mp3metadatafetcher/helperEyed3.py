import re
import eyed3
import os
import requests

from helperJson import convertStringToJson, saveJsonToFile
import musicbrainzngs

def saveAudioFile(audiofile):
    #audiofile.tag.save(version=(1,None,None))
    audiofile.tag.save(version=(2,3,0))

def getJsonFromComment(audiofile):
    comment = audiofile.tag.comments[0].text
    thisComment = comment.decode("utf-8")
    return convertStringToJson(thisComment)

def getAudioFile(mp3File):
    audiofile = None
    try:
        audiofile = eyed3.load(mp3File)
        if (audiofile.tag == None):
            audiofile.initTag()
            saveAudioFile(audiofile)
    except Exception as e:
        print ("- initializeMp3File: EXCEPTION " + str(e))
        print ("- initializing mp3 file for you")
        audiofile.initTag()
        saveAudioFile(audiofile)
    return audiofile

def getArtistAndTitle(mp3JsonInfo):

    if "metadataitunes" in mp3JsonInfo and len(mp3JsonInfo["metadataitunes"]) > 0:
        metadata = mp3JsonInfo["metadataitunes"]
        # Just take the first response and send it back
        myArtist = metadata[0]["artistName"]
        myTitle = metadata[0]["trackName"]
        return myArtist, myTitle

    if "metadatamusicbrainzngs" in mp3JsonInfo and len(mp3JsonInfo["metadatamusicbrainzngs"]) > 0:
        metadata = mp3JsonInfo["metadatamusicbrainzngs"]
        # Just take the first response and send it back
        myArtist = metadata[0]["artist-credit-phrase"]
        myTitle = metadata[0]["title"]
        return myArtist, myTitle

def getITunesCoverBig(response):
    urlFromAPI = response['artworkUrl100']
    url        = urlFromAPI.replace("/source/100x100bb.jpg","/source/3000x3000bb.jpg")

    return requests.get(url, stream=True).raw.data

def getITunesCoverSmall(response):
    url = response['artworkUrl30']
    return requests.get(url, stream=True).raw.data

#################################################################
def getMusicbrainzCover(releaseId,type):
    MB_USERAGGENT_NAME    = "Rui's new app"
    MB_USERAGGENT_VERSION = "0.4"
    MB_USERAGGENT_LINK    = "https://ourNewMusikApp.de"    
    musicbrainzngs.set_useragent(MB_USERAGGENT_NAME, MB_USERAGGENT_VERSION, MB_USERAGGENT_LINK)
    try:
        list = musicbrainzngs.get_image_list(releaseId)
        saveJsonToFile("images.json",list)
        urlCover=None
        urlIcon=None
        if "images" in list and len(list['images']) > 0:
            imageDetails = list['images'][0] 
            if "image" in imageDetails:
                urlCover = imageDetails["image"]
            else:
                if "thumbnails" in imageDetails and "large" in imageDetails["thumbnails"]:
                    urlCover = imageDetails["thumbnails"]["large"]
        if "thumbnails" in imageDetails and "small" in imageDetails["thumbnails"]:
            urlIcon = imageDetails["thumbnails"]["small"]

        if type == "icon":
            return requests.get(urlIcon, stream=True).raw.data
        else:
            return requests.get(urlCover, stream=True).raw.data



    except Exception as e:
        print (" - addCoverImageForReleaseId: EXCEPTION found")
        print ("   >> " + str(e))
        return None

def updateMp3WithMetadata(audiofile,metadata):
    
    if "metadataitunes" in metadata or "metadatamusicbrainzngs" in metadata:
        #thisJson = convertStringToJson(comment)

        if "metadataitunes" in metadata and len(metadata["metadataitunes"]) > 0:
            myData = metadata["metadataitunes"]
            # Just take the first response and send it back
            thisResponse = myData[0]

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
            audiofile.tag.images.set(3, cover, 'image/jpg', u"cover")            
            audiofile.tag.images.set(1, icon, 'image/jpg', u"icon")            
            #audiofile.tag.images.set(2, icon, 'image/jpg', u"othericon")            
            
            saveAudioFile(audiofile)
            return True

        if "metadatamusicbrainzngs" in metadata and len(metadata["metadatamusicbrainzngs"]) > 0:
            myData = metadata["metadatamusicbrainzngs"]
            # Just take the first response and send it back
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
                        audiofile.tag.images.set(3, cover, 'image/jpg', u"cover")            
                    cover = getMusicbrainzCover(releaseId,"icon")
                    if cover is not None:
                        audiofile.tag.images.set(1, cover, 'image/jpg', u"icon")            

                if ('medium-list' in thisResponse["release-list"][0]):
                    if len(thisResponse["release-list"][0]["medium-list"]) > 0:
                        entryMediumList = thisResponse["release-list"][0]["medium-list"]
                        if 'track-list' in entryMediumList[0] and len(entryMediumList[0]["track-list"]) > 0:
                            audiofile.tag.track = entryMediumList[0]["track-list"][0]["number"]
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
            return True


def addNameToImageIfMissing(audiofile):

    for image in audiofile.tag.images:
        type = image.type
        description = image.description
        print(audiofile.path + ": >" + str(type) + "< - >" + str(description) + "<")

