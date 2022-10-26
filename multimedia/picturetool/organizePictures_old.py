from asyncio import staggered
from curses.ascii import DEL
from distutils import filelist
from email.mime import base
from math import fabs
import os
import filetype
from GPSPhoto import gpsphoto
import os
import sys
from pathlib import Path
from datetime import datetime
from os.path import getmtime
import filetype
import dateutil.parser as parser
from exif import Image
import piexif
import json
import shutil
import ciso8601
from  itertools import chain

PIC_FOLDER = "/Users/d045023/bilder/sortiert/final"

FILE_WITH_METADATA = "metadata.json"

FILES_TO_BE_DELETED = [".DS_Store","Thumbs.db",".designerthumb"]

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


def getDuplicatesList(resultFile, result):
    file_exists = os.path.exists(resultFile)    

    if file_exists is False:
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
                splitter = file.split("/")
                filename = splitter[len(splitter) - 1]
                item.append(filename)
            result.append(item)
    return result


def deleteEmptyFolders(FOLDER):
    command = "find " + FOLDER + " -type d -empty -delete"
    print (command)
    os.system(command)


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


def getDateFromFilename(filename):
    dateInFilename = None
    thisDir, thisName, prefix, suffix = splitFileName(filename)

    try:
        temp1, temp2 = prefix.split("_")
        temp = temp1 + " " + temp2[0:2] + ":" + temp2[2:4] + ":" + temp2[4:6] 
        dateInFilename = parser.parse(temp, fuzzy=True).strftime('%Y:%m:%d %H:%M:%S')
        return dateInFilename   
    except:
        dateInFilename = None

    if dateInFilename is None:
        try:
            dateInFilename = parser.parse(prefix, fuzzy=True).strftime('%Y:%m:%d %H:%M:%S')
            return dateInFilename
        except:
            dateInFilename = None
    try:
        temp1, temp2 = prefix.split("_")
        temp = temp1 + " " + temp2[0:2] + ":" + temp2[3:5] + ":" + temp2[6:8] 
        dateInFilename = parser.parse(temp, fuzzy=True).strftime('%Y:%m:%d %H:%M:%S')
        return dateInFilename
    except:
        dateInFilename = None
    return dateInFilename


# Detect whether there is gps data in the file
def hasGpsData(filename):
    try:
        data = gpsphoto.getGPSData(filename)
        if data and "Latitude" in data or "Longitude" in data:
            return True
    except:
        return False

    return False


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


def getFileType(filename):
    typeString = "TBD"
    if filetype.is_image(filename):
        typeString = "PIC"
    if filetype.is_video(filename):
        typeString = "VID"
    if filetype.is_audio(filename):
        typeString = "AUD"
    return typeString


def getYoungestDate(dates):
    datePattern = '%Y:%m:%d %H:%M:%S'
    result = None
    dates = list(dict.fromkeys(dates))    

    for thisDate in dates:
        thisDate = thisDate.replace(": ", ":0")
        thisResult = datetime.strptime(thisDate, datePattern)
        if result is None:
            result = thisResult
        else:
            if thisResult < result:
                result = thisResult

    dateTimeString = None
    if result:
        dateTimeString = result.strftime(datePattern)
    return dateTimeString


# The youngest date will be taken
def determinePictureDate(filename):
    result = []
    tag_DateTimeOrig = None
    tag_DateTimeDigitized = None
    tag_DateTime = None
    lastModified = None
    dateInFilename = None

    try:
        with open(filename, "rb") as src:
            img = Image(src)
            tag_DateTimeOrig = img.datetime_original
            tag_DateTimeDigitized = img.datetime_digitized
            tag_DateTime = img.datetime
    except Exception as e :
       result = []
    
    if tag_DateTime is not None :
        result.append(tag_DateTime)

    if tag_DateTimeOrig is not None:
        result.append(tag_DateTimeOrig)

    if tag_DateTimeDigitized is not None:
        result.append(tag_DateTimeDigitized)

    dateInFilename = getDateFromFilename(filename)
    if dateInFilename is not None:
        result.append(dateInFilename)

    try:
        lastModified = datetime.fromtimestamp(getmtime(filename)).strftime('%Y:%m:%d %H:%M:%S')
    except:
        lastModified = None

    if lastModified is not None:
        result.append(lastModified)

    if result is None and len(result) == 0:
        print("ERROR: Could not get date from file >" + filename + "<")
        exit()

    finalResult = getYoungestDate(result)

    return finalResult


def getFileMetadata(FOLDER):
    fileWithMetadata = FILE_WITH_METADATA
    file_exists = os.path.exists(fileWithMetadata)    
    result = []

    if file_exists is False:
        checks = 0
        for subdir, dirs, files in os.walk(FOLDER):
            checks += len(files)

        i = 0
        for subdir, dirs, files in os.walk(FOLDER):
            for file in files:
                i += 1
                if subdir[-1] == "/":
                    sourcefile = subdir + file
                else:
                    sourcefile = subdir + "/" + file

                print("Analysing file " +str(i) + " of " +str(checks), end="\r")
                item = {}
                item["name"] = sourcefile
                item["fileType"] = getFileType(sourcefile)
                #item["hasGpsData"] = hasGpsData(sourcefile)
                item["pictureDate"] = determinePictureDate(sourcefile)
                result.append(item)
        saveJsonToFile(fileWithMetadata, result)
    else:
        result = getJsonFromFile(fileWithMetadata)
    return result


def getMetadaForFile(filename, filesMetadata):
    result = None
    for file in filesMetadata:
        if file.get("name") == filename:
            return file
    return result


# Deletes duplicates based on rules
def detectFilesToBeDeleted(duplicates, filesMetadata):
    fileWithMetadata = FILE_WITH_METADATA_ADDS
    file_exists = os.path.exists(fileWithMetadata)

    if file_exists == False:
        checks = len(duplicates)
        i = 0
        for fileList in duplicates:
            i += 1
            print("Duplicates check " + str(i) + " of " + str(checks))
            blocks = []
            if fileList and fileList != "":
                for file in fileList:
                    metadata = getMetadaForFile(file, filesMetadata)
                    blocks.append(metadata)
                dates = []
                # Fetch all picture dates and set default to not delete the file
                if blocks and len(blocks) > 1:
                    for block in blocks:
                        dates.append(block.get("pictureDate"))
                        block["tobedeleted"] = False
                    # Get youngest date
                    youngestDate = getYoungestDate(dates)
                    # Mark all files to be deleted that are older than the youngest date
                    markedOneFileToBeDeleted = False
                    for block in blocks:
                        if block.get("pictureDate") != youngestDate:
                            block["tobedeleted"] = True
                            markedOneFileToBeDeleted = True
                    # If the blocks have all the same date...
                    if markedOneFileToBeDeleted == False:
                        # .. check if there are entries with gps data
                        hasBlockWithGpsData = False
                        for block in blocks:
                            if block.get("hasGpsData") is True:
                                hasBlockWithGpsData = True
                        # .. if there is no gps data, simply mark the first one to be deleted
                        if hasBlockWithGpsData is False:
                            blocks[0]["tobedeleted"] = True
                        else:
                            # .. if there is gps data, simply mark all files to be deleted without gps data
                            for block in blocks:
                                if block.get("hasGpsData") is False:
                                    block["tobedeleted"] = True
                    # Ensure that only one file remains that will not be deleted
                    hasRemainingFile = False
                    for block in blocks:
                        if block.get("tobedeleted") == False and hasRemainingFile == False:
                            hasRemainingFile = True
                        if block.get("tobedeleted") == False and hasRemainingFile == True:
                            block.get("tobedeleted") == True

                    # Ensure that there is at least one file that won't be deleted
                    allFilesDeleted = True
                    for block in blocks:
                        toBeDeleted = block.get("tobedeleted")
                        if toBeDeleted == False:
                            allFilesDeleted = False
                    if allFilesDeleted == True:
                        print("ERROR: Issue in the script code, as it would delete all duplicate files.")
                        exit()

                    # Finally overwrite the metadata with the extracted deletion metadata
                    for block in blocks:
                        for file in filesMetadata:
                            if file.get("name") == block.get("name"):
                                file["tobedeleted"] = block.get("tobedeleted")
        
        saveJsonToFile(fileWithMetadata, filesMetadata)
        i = 0
        for file in filesMetadata:
            i += 1
            print("Final duplicates check " + str(i) + " of " + str(checks))
            basename = os.path.basename(file.get("name"))
            if basename in FILES_TO_BE_DELETED:
                file["tobedeleted"] = True
            # if there is no attribute to delete a file, than add it and set it to False
            if not file.get("tobedeleted"):
                file["tobedeleted"] = False

        saveJsonToFile(fileWithMetadata, filesMetadata)
    else:
        filesMetadata = getJsonFromFile(fileWithMetadata)


def addNewFilenamesToFiles(filesMetadata):
    fileWithMetadata = FILE_WITH_METADATA_TARGETFILES
    file_exists = os.path.exists(fileWithMetadata)

    if file_exists == False:
        targetFolder = TARGET_FOLDER
        checks = len(filesMetadata)

        i = 0
        for file in filesMetadata:
            i += 1
            print("Add new files. Check " + str(i) + " of " + str(checks))

            if file.get("tobedeleted") is not None and file.get("tobedeleted") == False:
                filename = file.get("name")

                dir, name, prefix, suffix = splitFileName(filename)
                pictureDate = file.get("pictureDate")

                my_time = datetime.strptime(pictureDate, '%Y:%m:%d %H:%M:%S')
                newTargetFolder = targetFolder + my_time.strftime('%Y/%m/%d/')
                typeString = file.get("fileType")

                suffix = suffix.lower().strip()
                suffix = suffix.replace("tiff","tif")
                suffix = suffix.replace("jpeg","jpg")

                newFilename = newTargetFolder + my_time.strftime(typeString+'%Y%m%d_%H%M%S') + suffix
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
        
        saveJsonToFile(fileWithMetadata, filesMetadata)
    else:
        filesMetadata = getJsonFromFile(fileWithMetadata)


def moveFiles(filesMetadata):
    deletion_folder = DELETION_FOLDER
    deletionCounter = 0

    # First move all files to the deletion folder, that can be deleted
    for file in filesMetadata:
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

    for file in filesMetadata:
        if file.get("targetName") is not None:
            dirname = os.path.dirname(file.get("targetName"))
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            # Before moving the file, update exif data for the picture date
            setExifDate(file.get("name"), file.get("pictureDate"))
            # Now move the file
            shutil.move(file.get("name"), file.get("targetName"))
            del file
 
def fixMp4File(filename):
    file, extension = os.path.splitext(filename)
    command = "ffmpeg -i '" + filename + "' -c copy '" + file + "FIX" + extension + "'"
    # print ("DEBUG >" + command + "<")
    os.system(command)


def convertMovToMP4(filename):
    file, extension = os.path.splitext(filename)
    command  ="ffmpeg -i '" + filename + "' -q:v 0 '" + file + "CONV.mp4'"
    os.system(command)


def removeEmptyFolders(src):
    print("Cleaning up folder structure")
    command = "find " + src + " -type d -empty -delete"
    print(command)
    os.system(command)

############################################################################
#removeEmptyFolders(PIC_FOLDER)

dupes = []

dupes = getDuplicatesList("dupes_log_temp1.txt", dupes)
dupes = getDuplicatesList("dupes_log_temp2.txt", dupes)
dupes = getDuplicatesList("dupes_log_temp3_one.txt", dupes)
dupes = getDuplicatesList("dupes_log_temp3_two.txt", dupes)
dupes = getDuplicatesList("dupes_temp5.txt", dupes)
dupes = getDuplicatesList("dupes_final.txt", dupes)


result = []
counterFiles = 0
for subdir, dirs, files in os.walk(PIC_FOLDER):    
    counterFiles += len(files)

counter = 0
for subdir, dirs, files in os.walk(PIC_FOLDER):
    for file in files:
        counter += 1
        print("Checking file " + str(counter) + " of " + str(counterFiles), end="\r")
        if file != ".DS_Store":
            uniqueFiles = set([thisFile for block in dupes for thisFile in block if file in block])
            if uniqueFiles and len(uniqueFiles) > 1:
                fileDate = ciso8601.parse_datetime(file[3:11].replace("_", " "))
                for uniqueFile in uniqueFiles:
                    try:
                        thisFileDate = ciso8601.parse_datetime(uniqueFile[3:11].replace("_", " "))
                        if thisFileDate < fileDate:
                            item = {}
                            item["file"] = file
                            item["older"] = uniqueFile
                            result.append(item)
                            print(file + ": " + uniqueFile)
                            break
                    except:
                        uniqueFile = uniqueFile

saveJsonToFile("fileNames.json", str(result))


#print("Detecting files to be deleted")
#detectFilesToBeDeleted(dupes, listMetadataFiles)

#print("Add new filenames")
#addNewFilenamesToFiles(listMetadataFiles)

#moveFiles(listMetadataFiles)

#removeEmptyFolders(PIC_FOLDER)
