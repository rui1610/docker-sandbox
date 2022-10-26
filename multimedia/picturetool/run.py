from exif import Image
from datetime import datetime
import time
import re
import os
import sys
import json
import shutil
import filetype
import ciso8601
import dateutil.parser as parser
from pathlib import Path
from  itertools import chain
from GPSPhoto import gpsphoto
import piexif


# https://stackify.com/20-simple-python-performance-tuning-tips/
# https://docs.python.org/3/library/stdtypes.html

year = "bilder"
MAIN_FOLDER = "/Users/d045023/bilder/"
PIC_FOLDER = MAIN_FOLDER + "zusortieren/" + year + "/"
TARGET_FOLDER = MAIN_FOLDER + "sortiert/" + year + "/"
DELETION_FOLDER = MAIN_FOLDER + "tobedeleted/"

FILE_WITH_DUPLICATES = "dupes_" + year + ".txt"

def deleteUnwantedFiles(FOLDER):
    unwantedFiles = ["*.DS_Store*","Thumbs.db",".designerthumb"]
    for filename in unwantedFiles:
        print ("Removing all files called '" + filename + "' in folder " + FOLDER)
        command = "find " + FOLDER + " -name '" + filename + "' -type f -delete"
        print (command)
        os.system(command)


def splitFileName(file):
    dir = os.path.dirname(os.path.realpath(file))
    name = Path(file).name
    prefix, suffix = os.path.splitext(file)
    return dir, name, prefix, suffix


def getJsonFromFile(fileObj):
    data = None
    foundError = False
    f = None

    filename = str(fileObj)

    try:
        f = open(filename, encoding="utf-8")
        data = json.load(f)
    except IOError:
        message = "Can't open json file >" + filename + "<"
        print(message)
        foundError = True
    except ValueError as err:
        message = "There is an issue in the json file >" + filename + \
            "<. Issue starts on character position " + \
            str(err.pos) + ": " + err.msg
        print(message)
        foundError = True
    finally:
        if f is not None:
            f.close()

    if foundError is True:
        message = "Can't continue the script before the error(s) mentioned above are not fixed"
        print(message)
        sys.exit(os.EX_DATAERR)
    return data


def saveJsonToFile(filename, jsonData):
    with open(filename, 'w') as outfile:
        json.dump(jsonData, outfile, indent=2)
    return True

# Detect whether there is gps data in the file
def hasGpsData(filename):
    try:
        data = gpsphoto.getGPSData(filename)
        if data and "Latitude" in data or "Longitude" in data:
            return True
    except:
        return False

    return False


def getDuplicatesList(resultFile):
    result = []

    #if file_exists is False:
    command = "fdupes -r " + PIC_FOLDER + " >" + resultFile
    print (command)
    os.system(command)

    data = Path(resultFile).read_text()
    if data and data != "":
        duplicateFiles = data.split("\n\n") 
        for block in duplicateFiles:
            item = []
            files = block.split("\n")
            for file in files:
                item.append(file)
            result.append(item)
    return result


def convertStringtimeToTimestamp(stringTime):
    cleanedDate = stringTime.replace(":", "")
    return ciso8601.parse_datetime(cleanedDate)


def getFileType(filename):
    typeString = "TBD"
    if filetype.is_image(filename):
        typeString = "PIC"
    if filetype.is_video(filename):
        typeString = "VID"
    if filetype.is_audio(filename):
        typeString = "AUD"
    return typeString


def getPictureDate(filename):
    date1 = datetime.now()
    date2 = date1
    date3 = date1
    date4 = date1
    exifDate = None
    datePatternTags = '%Y:%m:%d %H:%M:%S'
    datePatternFilename = '%Y%m%d_%H%M%S'

    allDates = []
    try:
        with open(filename, "rb") as src:
            img = Image(src)
            date1 = convertStringtimeToTimestamp(img.datetime_original)
            date2 = convertStringtimeToTimestamp(img.datetime_digitized)
            date3 = convertStringtimeToTimestamp(img.datetime)

            exifDate = min(date1, date2, date3)
    except Exception as e :
       result = None
    
    try:
        match = re. search(r'\d{4}\d{2}\d{2}_\d{2}\d{2}\d{2}',os.path.basename(filename))
        date4 = parser.parse(match.group(), fuzzy=True).strftime('%Y%m%d_%H%M%S')
        date4 = convertStringtimeToTimestamp(date4.replace("_", " "))
    except Exception as e :
        try:
            date4 = parser.parse(os.path.basename(filename)[0:18], fuzzy=True).strftime('%Y%m%d_%H%M%S')
            date4 = convertStringtimeToTimestamp(date4.replace("_", " "))
        except Exception as e :
            result = None
    
    #if exifDate is not None:
    #   return exifDate

    return min(date1, date2, date3, date4, datetime.now())

def getPicMetadata(filename, listDuplicates):
    result = {}
    result["name"] = filename
    result["date"] = getPictureDate(filename)
    result["filetype"] = getFileType(filename)
    result["hasGpsData"] = hasGpsData(filename)

    # If the file is not a duplicate it doesn't have to be deleted
    # If it is, the "tobedeleted" attribute won't be set, yet
    if filename not in chain(*listDuplicates):
        result["tobedeleted"] = False

    return result

def selectBestFileToKeep(pics):
    # Take the first file as a default value
    picToKeep = pics[0]

    minDate = datetime.now()
    for pic in pics:
        if pic.get("date") < minDate:
            minDate = pic.get("date")
            picToKeep = pic
        # If the file has hps data, always prefer that one (ignoring the date from before)
        if pic.get("hasGpsData"):
            picToKeep = pic

    picsToDelete = [thisPic for thisPic in pics if thisPic.get("name") != picToKeep.get("name")]
    return picToKeep, picsToDelete


def detectFilesToBeDeleted(picMetadata, listDuplicates):
    print("Detecting files to be deleted")
    for block in listDuplicates:
        thesePics = [thisPic for thisPic in picMetadata if thisPic.get("name") in block]
        if thesePics and len(thesePics) > 1:
            picToKeep, picsToDelete = selectBestFileToKeep(thesePics)

            # Update the "tobedeleted" attribute in the picMetadata list for the file to be kept
            pic = [thisPic for thisPic in picMetadata if thisPic.get("name") == picToKeep.get("name")]
            pic[0]["tobedeleted"] = False

            # Update the "tobedeleted" attribute in the picMetadata list for the file to be kept
            counter = 0
            for myPic in picsToDelete:
                counter += 1
                pic = [thisPic for thisPic in picMetadata if thisPic.get("name") == myPic.get("name")]
                pic[0]["tobedeleted"] = True
                print("Marked to be deleted (nr." + str(counter) + "): " + myPic.get("name"))
                #os.remove(pic[0]["name"])
                #del pic[0]


def addTargetFilenames(filesMetadata):
    print("Adding target file names")
    targetFolder = TARGET_FOLDER
    checks = len(filesMetadata)

    i = 0
    for file in filesMetadata:
        i += 1
        print("Add new files. Check " + str(i) + " of " + str(checks))

        if file.get("tobedeleted") is not None and file.get("tobedeleted") == False:
            filename = file.get("name")

            dir, name, prefix, suffix = splitFileName(filename)
            pictureDate = file.get("date")

            my_time = pictureDate.strftime('%Y:%m:%d %H:%M:%S')

            #my_time = datetime.strptime(pictureDate, '%Y:%m:%d %H:%M:%S')
            newTargetFolder = targetFolder + pictureDate.strftime('%Y/%m/%d/')
            typeString = file.get("filetype")

            suffix = suffix.lower().strip()
            suffix = suffix.replace("tiff","tif")
            suffix = suffix.replace("jpeg","jpg")

            if suffix:
                newFilename = newTargetFolder + pictureDate.strftime(typeString + '%Y%m%d_%H%M%S') + suffix
                file["targetName"] = newFilename

    # In case a filename is already taken, add a suffix
    allTargetFilenames = []
    i = 0
    for file in filesMetadata:
        i += 1
        print("Check if file already available. Check " + str(i) + " of " + str(checks))
        if file.get("tobedeleted") is not None and file.get("tobedeleted") is False:
            newFilename = file.get("targetName")
            if newFilename is not None:
                if newFilename not in allTargetFilenames:
                    allTargetFilenames.append(newFilename)
                else:
                    for j in range(1, 999):
                        dir, name, prefix, suffix = splitFileName(newFilename)
                        newFilenameTry = prefix + "_" + str(j) + suffix
                        if newFilenameTry not in allTargetFilenames:
                            file["targetName"] = newFilenameTry
                            allTargetFilenames.append(newFilenameTry)
                            break


def setExifDate(filename, new_date):

    try:
        exif_dict = piexif.load(filename)
        exif_dict['0th'][piexif.ImageIFD.DateTime] = new_date
        exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = new_date
        exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = new_date
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, filename)
    except:
        new_date = new_date


def moveFiles(filesMetadata):
    deletion_folder = DELETION_FOLDER
    deletionCounter = 0
    print("Moving files. First the ones to be deleted")

    # First move all files to the deletion folder, that can be deleted
    counterFiles = len(filesMetadata)
    counter = 0
    for file in filesMetadata:
        counter += 1
        print(" - analyse and move file " + str(counter) + " of " + str(counterFiles), end="\r")
        if file.get("tobedeleted") is not None and file.get("tobedeleted") == True:
            dirname = os.path.dirname(deletion_folder)
            deletionCounter += 1
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            basename = os.path.basename(file.get("name"))
            counterString = str(deletionCounter).zfill(7)
            filenameDeletionFolder = dirname + "/" + counterString + "_" + basename
            shutil.move(file.get("name"), filenameDeletionFolder)
            del file

    print("Moving files. Now the ones to keep")
    counterFiles = len(filesMetadata)
    counter = 0
    for file in filesMetadata:
        counter += 1
        print(" - analyse and move file " + str(counter) + " of " + str(counterFiles), end="\r")
        if file.get("targetName") is not None:
            dirname = os.path.dirname(file.get("targetName"))
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            # Before moving the file, update exif data for the picture date
            setExifDate(file.get("name"), file.get("pictureDate"))
            # Now move the file
            shutil.move(file.get("name"), file.get("targetName"))
            del file


def getPicMetadataForAllFiles(root_folder, listDuplicates):
    result = []

    counterFiles = 0
    for dirpath, dirnames, filenames in os.walk(root_folder):
        counterFiles += len(filenames)
    print('Found files:' + str(counterFiles))

    counter = 0
    for dirpath, dirnames, filenames in os.walk(root_folder):
        for thisFile in filenames:
            counter += 1
            print("Get metadata for file " + str(counter) + " of " + str(counterFiles) + " (" + thisFile + ")", end="\r")
            result.append(getPicMetadata(dirpath + "/" + thisFile, listDuplicates))
    return result

def removeEmptyFolders(src):
    print("Cleaning up folder structure")
    command = "find " + src + " -type d -empty -delete"
    print(command)
    os.system(command)

#deleteUnwantedFiles(MAIN_FOLDER)

duplicates = getDuplicatesList(FILE_WITH_DUPLICATES)
picMetadata = getPicMetadataForAllFiles(PIC_FOLDER, duplicates)

detectFilesToBeDeleted(picMetadata, duplicates)
addTargetFilenames(picMetadata)

moveFiles(picMetadata)
removeEmptyFolders(MAIN_FOLDER)

