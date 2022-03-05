import errno
import shutil, sys 
import os
import glob, time
from pathlib import Path 
from datetime import datetime
from os.path import getmtime
#import PIL
import filetype
import dateutil.parser as parser
from exif import Image
import piexif
import mutagen

sourceFolder = "/picturetool/source"
targetFolder = "/picturetool/target"
DEFAULTDATE="AUTO"
FIXEDDATE=None

def buildNewPictureFilename(filename,pictureDate,typeString):
    dir,name,prefix,suffix = splitFileName(filename)
    my_time = datetime.strptime(pictureDate, '%Y:%m:%d %H:%M:%S')
    newTargetFolder=targetFolder + "/bilder/" + my_time.strftime('%Y/%m/%d/')
    if not os.path.exists(newTargetFolder):
        os.makedirs(newTargetFolder)

    newFilename=newTargetFolder + my_time.strftime(typeString+'%Y%m%d_%H%M%S')  + "." + suffix

    # If the file already exists, add a suffix to the name with the current timestamp
    if os.path.isfile(newFilename):
        now = datetime.now()
        temp = now.strftime("%H%M%S%f")
        newFilename=newTargetFolder + typeString + my_time.strftime('%Y%m%d_%H%M%S') + "_TMP" + temp + "." + suffix
        print("- FILENAMEBUILDINFO: File was already existing. Added the current timestamp as suffix " + newFilename)
    return  newFilename

def getDateFromFilename(filename):
    dateInFilename=None
    thisDir, thisName, prefix , suffix = splitFileName(filename)

    try:
        temp1,temp2=prefix.split("_")
        temp=temp1 + " " + temp2[0:2] + ":" +  temp2[2:4] + ":" + temp2[4:6] 
        dateInFilename=parser.parse(temp,fuzzy=True).strftime('%Y:%m:%d %H:%M:%S')
        #print (" - DEBUG date from filename >" + str(dateInFilename) + "<")
        return dateInFilename        
    except:
        dateInFilename=None

    if dateInFilename is None:
        try:
            dateInFilename=parser.parse(prefix,fuzzy=True).strftime('%Y:%m:%d %H:%M:%S')
            #print (" - DEBUG date from filename >" + str(dateInFilename) + "<")
            return dateInFilename        
        except:
            dateInFilename=None

    try:
        temp1,temp2=prefix.split("_")
        temp=temp1 + " " + temp2[0:2] + ":" +  temp2[3:5] + ":" + temp2[6:8] 
        dateInFilename=parser.parse(temp,fuzzy=True).strftime('%Y:%m:%d %H:%M:%S')
        #print (" - DEBUG date from filename >" + str(dateInFilename) + "<")
        return dateInFilename        
    except:
        dateInFilename=None

    #print (" - DEBUG date from filename >" + str(dateInFilename) + "<")
    return dateInFilename        


def getPicureDate(filename):
    returnValue=None
    tag_DateTimeOrig=None
    tag_DateTimeDigitized=None
    tag_DateTime=None
    lastModified=None
    dateInFilename=None

    if FIXEDDATE is not None:
        setExif(filename, FIXEDDATE)
        return FIXEDDATE

    if DEFAULTDATE == "FILENAME":
        dateInFilename=getDateFromFilename(filename)
        if dateInFilename is not None:
            print("- PICTUREDATE: Using date in file name " + filename + " >" + str(dateInFilename) + "<")
            setExif(filename, dateInFilename)
            return dateInFilename
    try:
        with open(filename, "rb") as src:
            img = Image(src)
            #test = img.list_all()
            tag_DateTimeOrig = img.datetime_original
            tag_DateTimeDigitized= img.datetime_digitized
            tag_DateTime= img.datetime
            gps_timestamp=img.gps_timestamp
            gps_map_datum=img.gps_map_datum
            gps_datestamp=img.gps_datestamp
            print ("DEBUG EXIFDATA tag_DateTimeOrig: " + str(tag_DateTimeOrig))
            print ("DEBUG EXIFDATA tag_DateTimeDigitized: " + str(tag_DateTimeDigitized))
            print ("DEBUG EXIFDATA tag_DateTime: " + str(tag_DateTime))
            print ("DEBUG EXIFDATA gps_timestamp: " + str(gps_timestamp))
            print ("DEBUG EXIFDATA gps_map_datum: " + str(gps_map_datum))
            print ("DEBUG EXIFDATA gps_datestamp: " + str(gps_datestamp))
    except :
        returnValue = returnValue

        # print ("DEBUG00:" +filename + " >" + str(dateInFilename))
        # print ("DEBUG0:" +filename + " >" + str(lastModified))
        # print ("DEBUG1:" +filename + " >" + str(tag_DateTime))
        # print ("DEBUG2:" +filename + " >" + str(tag_DateTimeOrig))
        # print ("DEBUG3:" +filename + " >" + str(tag_DateTimeDigitized))
 
        # for tag, value in exifdata.items():
        #     decodedTag = ExifTags.TAGS.get(tag, tag)
        #     exifdata[decodedTag] = value
        #     print (" - " + str(exifdata[decodedTag]) + ": " + str(value))


    if tag_DateTime is not None:
        print("- PICTUREDATE: Using EXIF date time >" + str(tag_DateTime) + "<")
        return tag_DateTime

    if tag_DateTimeOrig is not None:
        print("- PICTUREDATE: Using EXIF original date time >" + str(tag_DateTimeOrig) + "<")
        return tag_DateTimeOrig

    if tag_DateTimeDigitized is not None:
        print("- PICTUREDATE: Using EXIF date time digitized >" + str(tag_DateTimeDigitized) + "<")
        return tag_DateTimeDigitized

    dateInFilename=getDateFromFilename(filename)
    if dateInFilename is not None:
        print("- PICTUREDATE: Using date in file name " + filename + " >" + str(dateInFilename) + "<")
        setExif(filename, dateInFilename)
        return dateInFilename

    try:
        lastModified=datetime.fromtimestamp(getmtime(filename)).strftime('%Y:%m:%d %H:%M:%S')
    except:
        lastModified=None

    if lastModified is not None:
        print("- PICTUREDATE: Using last modified date >" + str(lastModified) + "<")
        setExif(filename, lastModified)
        return lastModified

    if returnValue is None:
        print("ERROR: Could not get date from file >" + filename + "<")
        removeEmptyFolders(sourceFolder)
        exit()

    return returnValue

def setExif(filename,new_date):

    try:
        exif_dict = piexif.load(filename)
        exif_dict['0th'][piexif.ImageIFD.DateTime] = new_date
        exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = new_date
        exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = new_date
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, filename)
    except:
        new_date = new_date




def movePicture(root, filename, typeString):

    print ("INFO Source: " + filename)

    origFilename = os.path.join(root,filename)
    creation_time = None
    picDate=getPicureDate(origFilename)

    newFilename = buildNewPictureFilename(origFilename,picDate,typeString)

    print ("INFO Target: " + newFilename)
    print ("#####################################")
    shutil.move(filename,newFilename)

def moveFiles():
      
    for root, directories, filenames in os.walk(sourceFolder):
        i = 0
        test=len(filenames)
        print("Files: " + str(test))
        for filename in filenames:
            i+=1
            print ("File number " + str(i))
            ## Check if file is a picture
            thisFile = os.path.join(root,filename)
            if filetype.is_image(thisFile):
                movePicture(root,thisFile,"PIC")
                continue
            if filetype.is_video(thisFile):
                movePicture(root,thisFile,"VID")
                continue
            if filetype.is_audio(thisFile):
                movePicture(root,thisFile,"AUD")
                continue

def fixMp4File(filename):
    file, extension = os.path.splitext(filename)
    command="ffmpeg -i '" + filename + "' -c copy '" + file + "FIX" + extension + "'"
    #print ("DEBUG >" + command + "<")
    os.system(command)

def convertMovToMP4(filename):
    file, extension = os.path.splitext(filename)
    command="ffmpeg -i '" + filename + "' -q:v 0 '" + file + "CONV.mp4'"
    #print ("DEBUG0 >" + command + "<")
    os.system(command)
    exit()


def makeSuffixLowerCase(root,filename):
    oldFilename = os.path.join(root,filename) 

    file, extension = os.path.splitext(oldFilename)

    if extension != extension.lower():
        filenameNew = os.path.join(root,filename.lower())
        file, extension = os.path.splitext(oldFilename)
        filenameNew = file + "new"+ extension.lower()
        command = 'mv "' + oldFilename + '"  "' + filenameNew + '"'
        print (command)
        os.system(command)


def removeDuplicates(src):
    print ("- Removing duplicate files in target folder")
    command = 'fdupes -rdN ' + src
    os.system(command)

    #find .  -size -50k -delete
    command = "find " + src + " -type d -empty -delete"
    print (command)
    os.system(command)

    command = "find " + src + " -size -50k -delete"
    print (command)
    os.system(command)

def splitFileName(file):
    dir = os.path.dirname(os.path.realpath(file))


    name = Path(file).name
    #prefix, suffix = name.split(".")
    prefix, suffix = os.path.splitext(file)

    return dir,name,prefix,suffix


def deleteUnwantedFiles(src,unwantedFiles):
    for filename in unwantedFiles:
        print ("Removing all files called '" + filename + "' in folder " + src)
        command = "find " + src + " -name '" + filename + "' -type f -delete"
        print (command)
        os.system(command)

def makeAllFileSuffixLowerCase(src):
    print ("Now making all file suffix lower case")
    for root, directories, filenames in os.walk(src):
        for filename in filenames:

            makeSuffixLowerCase(root,filename)

    print ("DONE. Made all file suffix lower case")


def moveFileTypes(src,target,fileTypes):
    print ("Now move all files from source " + src + " to " + target )
        
    if not os.path.exists(target):
        os.makedirs(target)
    for root, directories, filenames in os.walk(src):
        i = 0
        for filename in filenames:

            oldFilename = os.path.join(root,filename)

            filenameNoExt, file_extension = os.path.splitext(filename)
            if (file_extension in fileTypes):
                i = i + 1
                filenameNew = target  + "/" + filenameNoExt +  str(i) + file_extension
                command = 'mv "' + oldFilename + '"  "' + filenameNew + '"'
                print (command)
                os.system(command)
    print ("DONE. Moved all files to " + target)

def removeEmptyFolders(src):
    print ("Cleaning up folder structure")
    command = "find " + src + " -type d -empty -delete"
    print (command)
    os.system(command)

def renameFiles(src,srcFormat,targetFormat):
    command = "find " + src + " -depth -name \"*." + srcFormat + "\" -exec sh -c 'mv \"$1\" \"${1%." + srcFormat + "}." + targetFormat + "\"' _ {} \;"
    print(command)
    os.system(command)

#################################################################################
parameter  = None
parameter2 = None

if (len(sys.argv) == 2):
    parameter = sys.argv[1]

if (len(sys.argv) == 3):
    parameter2 = sys.argv[2]

if (parameter is not None and parameter == "FILENAME"):
    print("Will force files to get their timestamp from the FILENAME")
    DEFAULTDATE="FILENAME"

if (parameter is not None and parameter == "FIXEDDATE" and parameter2 is not None):
    DEFAULTDATE="FIXEDDATE"
    print("Will force files to set their timestamp to the fixed value of >" + str(FIXEDDATE) + "<")
    FIXEDDATE=parameter2

removeEmptyFolders(sourceFolder)
deleteUnwantedFiles(sourceFolder,[".DS_Store","Thumbs.db",".designerthumb"])
makeAllFileSuffixLowerCase(sourceFolder)

renameFiles(sourceFolder,"tiff","tif")
renameFiles(sourceFolder,"jpeg","jpg")
moveFiles()
removeEmptyFolders(sourceFolder)

#removeDuplicates(sourceFolder)
