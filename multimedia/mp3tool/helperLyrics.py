import requests
import re

from helperEyed3 import saveAudioFile

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
    if findStart > 0:
        startLyrics = content.find(findStart) + len(findStart)
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

    for lyric in lyrics:
        print (lyric)


def addLyrics(audiofile):

    deleteLyricsIfContainingHtmlTags(audiofile)

    url = prepareSearchUrl(audiofile)
    content = getPageContent(url)
    lyrics = getLyricsFromUrlContent(content)
    if lyrics is not None:
        audiofile.tag.lyrics.set('"' + lyrics + '"')
        saveAudioFile(audiofile)



