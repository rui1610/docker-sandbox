import errno
import shutil, sys 
import os
import re
from pathlib import Path 
from datetime import datetime
from os.path import getmtime
import filetype
from  geopy.geocoders import Nominatim
from fractions import Fraction
from GPSPhoto import gpsphoto
import dateutil.parser as parser
from PIL import Image

sourceFolder = "/picturetool/input"

# https://pypi.org/project/gpsphoto/
def get_gps_location(filename):
    data = gpsphoto.getGPSData(filename)
    latitude = None
    longitude = None
    if "Latitude" in data:
        latitude  = data["Latitude"]
    if "Longitude" in data:
        longitude = data["Longitude"]
    return latitude, longitude

# https://pypi.org/project/gpsphoto
def set_gps_location(filename,latitude,longitude):
    photo = gpsphoto.GPSPhoto(filename)
    info = gpsphoto.GPSInfo((latitude, longitude))
    photo.modGPSData(info, filename)

def getGPSFile(filename):
    dir,name,prefix,suffix = splitFileName(filename)
    gpsFile=dir + "/" + prefix + ".gps"
    if os.path.isfile(gpsFile):
        return gpsFile
    return None

def addGPSDataFromFile(filename,filenameGPSData):
    if (filenameGPSData is None):
        return None
    data=None
    try:
        geolocator = Nominatim(user_agent="picturetool-rui")
        text = open(filenameGPSData, "r")
        data = text.read()
        loc = geolocator.geocode(data)
        latitude = loc.latitude
        longitude= loc.longitude
        #print("GPS DATA for >" + data + "<: latitude=" + str(loc.latitude) + "< and longtitude >" + str(loc.longitude) + "<")
        set_gps_location(filename,latitude,longitude)
        print(" - done: added GPS data in file >" + filename + "< for >" + data + "<")
    except Exception as e:
        print("ERROR: Could not get GPS data for >" + filenameGPSData + "<")
        print(e)
        exit()

# Finds out from the string, whether GPS coordinates or an address has been entered
def determineCoordinates(data):

    latitude = None
    longitude= None

    coords = re.match('/(-?\d+\.\d+),(-?\d+\.\d+)/', data)

    if (coords is not None):
        latitude = loc.latitude
        longitude= loc.longitude
    else:
        geolocator = Nominatim(user_agent="picturetool-rui")
        loc = geolocator.geocode(data)
        latitude = loc.latitude
        longitude= loc.longitude

    return latitude, longitude

def addGPSDataFromString(filename,location):
    if (location is None):
        return None
    data=None
    try:
        latitude, longitude = determineCoordinates(location)
        print("GPS DATA for >" + location + "<: latitude=" + str(latitude) + "< and longtitude >" + str(longitude) + "<")
        set_gps_location(filename,latitude,longitude)
        print(" - done: added GPS data in file >" + filename + "< for >" + location + "<")
        dir,name,prefix,suffix = splitFileName(filename)
    except Exception as e:
        print("ERROR: Could not get GPS data for >" + location + "<")
        print(e)
        exit()
    #Delete GPSFile if successfull!


def splitFileName(file):
    dir = os.path.dirname(os.path.realpath(file))
    name = Path(file).name
    prefix, suffix = name.split(".")
    return dir,name,prefix,suffix

def addToFileList(filenameList,file,date,latitude,longitude):
    file = file

def getFileMetadata(filename):

    datetimePic=None
    longitude=None
    latitude=None
    altitude=None
    date = None
    utctime = None

    try:
        im = Image.open(filename)
        exif = im.getexif()
        datetimePic = exif.get(36867)
    except:
        datetimePic=None

    data = gpsphoto.getGPSData(thisFile)

    mainFilenamePart=filename[0:18]
    timestamoInFilename=parser.parse(mainFilenamePart,fuzzy=True).strftime('%Y:%m:%d %H:%M:%S')

    if "Date" in data:
        date = data["Date"]
    if "UTC-Time" in data:
        utctime = data["UTC-Time"]
    if "Longitude" in data:
        longitude = data["Longitude"]
    if "Latitude" in data:
        latitude = data["Latitude"]
    if "Altitude" in data:
        altitude = data["Altitude"]

    returnValue=str(filename) + ";" + str(datetimePic) + ";" + str(utctime) + ";" + str(date) + ";" + str(latitude) + ";" + str(longitude)

    return returnValue



def checkAndUpdateMetadataInPicture(filename):

    mainFilenamePart=filename[0:18]
    timestamoInFilename=parser.parse(mainFilenamePart,fuzzy=True).strftime('%Y:%m:%d %H:%M:%S')

    data = gpsphoto.getGPSData(thisFile)
    longitude=None
    latitude=None
    altitude=None
    date = None
    utctime = None
    
    if "Date" in data:
        date = data["Date"]
    if "UTC-Time" in data:
        utctime = data["UTC-Time"]
    if "Longitude" in data:
        longitude = data["Longitude"]
    if "Latitude" in data:
        latitude = data["Latitude"]
    if "Altitude" in data:
        altitude = data["Altitude"]

    print("Date " + str(date) + " - utctime " +str(utctime) + " - latitude " + str(latitude) + " - longitude " + str(longitude))  

    if (date is None or utctime is None) and (latitude is not None and longitude is not None):
        photo = gpsphoto.GPSPhoto(thisFile)
        if altitude is None:
            altitude = int(0)
        info = gpsphoto.GPSInfo((longitude, latitude), timeStamp=timestamoInFilename)
        photo.modGPSData(info, thisFile)

#################################################################################

parameter  = None
parameter2 = None
parameter3 = None

if (len(sys.argv) == 2):
    parameter = sys.argv[1]

if (len(sys.argv) == 4 ):
    parameter = sys.argv[1]
    parameter2 = sys.argv[2]
    parameter3 = sys.argv[3]

if (parameter == "FILE"):
    thisFile = parameter2
    data = parameter3

    if filetype.is_image(thisFile):
        addGPSDataFromString(thisFile,data)

if (parameter == "CREATEFILELIST"):
    logfile = open("filelist.csv", "a")
    for root, directories, filenames in os.walk(sourceFolder):
        i = 0
        for filename in filenames:
            ## Check if file is a picture
            thisFile = os.path.join(root,filename)
            if filetype.is_image(thisFile):
                data=getFileMetadata(filename)
                print("File " + thisFile)
                logfile.write(data + "\n")
    logfile.close()

if (parameter == "FOLDER"):
    sourceFolder = parameter2
    data = parameter3
    print("INFO: Will now scan all files in folder >" + sourceFolder + "< and add GPS data for location >" + data + "<")

    for root, directories, filenames in os.walk(sourceFolder):
        i = 0
        for filename in filenames:
            ## Check if file is a picture
            thisFile = os.path.join(root,filename)
            if filetype.is_image(thisFile):
                print(" - checking >" + thisFile + "<")
                addGPSDataFromString(thisFile,data)


if (parameter is None and parameter2 is None and parameter3 is None):
    print("INFO: Will now scan all files in folder >" + sourceFolder + "< and add GPS data from potentially existing gps files")

    for root, directories, filenames in os.walk(sourceFolder):
        i = 0
        for filename in filenames:
            ## Check if file is a picture
            thisFile = os.path.join(root,filename)
            if filetype.is_image(thisFile):
                print("CHECK FOR GPS DATA in >" + thisFile + "<")
                latitude,longitude = get_gps_location(thisFile)
                if (latitude is None and latitude is None):
                    filenameGPSData=getGPSFile(thisFile)
                    addGPSDataFromFile(thisFile,filenameGPSData)
                else:
                    print(" - GPS DATA already available in this file")

if (parameter is not None and parameter2 is None and parameter3 is None):
    print("INFO: Will now scan all files in folder >" + parameter + "< and add GPS data from potentially existing gps files")

    for root, directories, filenames in os.walk(parameter):
        i = 0
        for filename in filenames:
            ## Check if file is a picture
            thisFile = os.path.join(root,filename)
            if filetype.is_image(thisFile):
                print("CHECK FOR GPS DATA in >" + thisFile + "<")
                latitude,longitude = get_gps_location(thisFile)
                if (latitude is None and latitude is None):
                    filenameGPSData=getGPSFile(thisFile)
                    addGPSDataFromFile(thisFile,filenameGPSData)
                else:
                    print(" - GPS DATA already available in this file")                    
