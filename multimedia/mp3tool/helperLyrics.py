from curses import meta
import requests
import re
import os
import time
from lyricsgenius import Genius
from helperEyed3 import getImageDescriptionForType, saveAudioFile
from helperGeneric import hasArtist, hasCover, hasLyrics, hasTitle

GENIUS_ACCESS_TOKEN = os.getenv('GENIUS_ACCESS_TOKEN')
genius = Genius(GENIUS_ACCESS_TOKEN)
genius.excluded_terms = ["(Remix)", "(Live)"]
genius.remove_section_headers = True
genius.skip_non_songs = True

def getPageContent(url):

    try:
        response = requests.get(url)
        if response.status_code == 200:
            thisContent = response.content.decode("utf-8")
            return thisContent
        else:
            return None

    except Exception as e:
        print (" - addItunesCoverArt: EXCEPTION found")
        print ("   >> request: " + url)
        print ("   >> " + str(e))
        return None

def prepareSearchUrl(audiofile):

    artist = str(audiofile.tag.artist.lower())
    title = str(audiofile.tag.title).lower()

    song = re.sub('[^0-9a-zA-Z]+', '', title) 
    artist = re.sub('[^0-9a-zA-Z]+', '', artist) 
    url = "http://www.azlyrics.com/lyrics/" + artist + "/" + song + ".html"

    return url


def getLyricsFromUrlContent(content):

    result = None

    findStart = "<!-- Usage of azlyrics.com content by any third-party lyrics provider is prohibited by our licensing agreement. Sorry about that. -->"
    startLyrics = content.find(findStart) + len(findStart)
    if startLyrics > len(findStart):
        lyricsText = content[startLyrics:]
        findEnd = "</div>"
        endLyrics = lyricsText.find(findEnd) 
        theseLyrics = lyricsText[:endLyrics]
        theseLyrics = theseLyrics.replace("\r\n", "\n")
        theseLyrics = theseLyrics.replace("<br>", "")
        result = theseLyrics

    return result

def deleteLyricsIfContainingHtmlTags(audiofile):
    lyrics = audiofile.tag.lyrics
    
    tagsToCheck = ["</title>", "</script>", "</head>"]

    htmlFound = False
    for lyric in lyrics:
        text = lyric.text

        for tag in tagsToCheck:
            if tag in text:
                htmlFound = True

        if htmlFound == True:
            audiofile.tag.lyrics.set("")
            saveAudioFile(audiofile)


# def addLyrics(audiofile):

#     lyrics = getLyricsFromGenius(audiofile)

#     if lyrics is not None:
#         audiofile.tag.lyrics.set('"' + lyrics + '"')
#         saveAudioFile(audiofile)
#     else:
#         deleteLyricsIfContainingHtmlTags(audiofile)

#         url = prepareSearchUrl(audiofile)
#         content = getPageContent(url)
#         lyrics = getLyricsFromUrlContent(content)
#         if lyrics is not None:
#             audiofile.tag.lyrics.set('"' + lyrics + '"')
#             saveAudioFile(audiofile)


def getSongInfoFromGenius(audiofile):
    if GENIUS_ACCESS_TOKEN is None or GENIUS_ACCESS_TOKEN == "":
        print("Missing GENIUS_ACCESS_TOKEN as env variable. Skipping search for lyrics on genius API.")
        return None

    try:
        song = genius.search_song(title=audiofile.tag.title, artist=audiofile.tag.artist, get_full_info=True)

        if song is not None:
            return song
        else:
            return None
    except Exception as e:
        print("WARNING: Timeout execption on genius API. No lyrics collected: " + str(e))
        #anotherTry = getSongInfoFromGenius(audiofile)

        return None

def addMetadataFromGenius(audiofile):

    if hasArtist(audiofile) and hasTitle(audiofile):
        if hasLyrics(audiofile) is False:
            metadata = getSongInfoFromGenius(audiofile)
            if metadata is not None:
                lyrics = metadata.lyrics
                audiofile.tag.lyrics.set('"' + lyrics + '"')
        # if hasCover(audiofile) is False:
        #     metadata = getSongInfoFromGenius(audiofile)
        #     if metadata is not None:
        #         cover = requests.get(metadata.song_art_image_url, stream=True).raw.data
        #         icon = requests.get(metadata.song_art_image_thumbnail_url, stream=True).raw.data
        #         imageType = 3
        #         audiofile.tag.images.set(imageType, cover, 'image/jpg', getImageDescriptionForType(imageType))            
        #         imageType = 1
        #         audiofile.tag.images.set(imageType, icon, 'image/jpg', getImageDescriptionForType(imageType))            
        saveAudioFile(audiofile)
