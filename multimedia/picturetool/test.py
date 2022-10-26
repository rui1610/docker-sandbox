import json
import sys, os
from datetime import datetime
import shutil


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

files = getJsonFromFile("fileNames.json")

print("Will rename " + str(len(files)) + " files")

counter = 0
for thisFile in files:
    counter += 1
    folder = "/Users/d045023/bilder/sortiert/final/"
    pictureDate = thisFile["file"][3:18]

    my_time = datetime.strptime(pictureDate, '%Y%m%d_%H%M%S')
    newTargetFolder = folder + my_time.strftime('%Y/%m/%d/')

    initialFilename = newTargetFolder + thisFile["older"]
    newFilename = newTargetFolder + thisFile["file"]

    try:
        shutil.move(initialFilename, newFilename)
        print(str(counter) + ": " + initialFilename + " to " + newFilename)
    except:
        print(str(counter) + ": can't rename file " + thisFile["file"])
