from fileinput import filename
from pathlib import Path
import os
from  itertools import chain
import shutil

def readDupes(resultFile):
    result = []
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


dupes = readDupes("dupes_log_temp2.txt")

FOLDER = "/Users/d045023/bilder/sortiert/temp2/2022"

fileCounter = 0
lenCheckString = 11
for dirpath, dirnames, filenames in os.walk(FOLDER):
    for thisFile in filenames:
        print("Check file " + thisFile, end="\r")
        for block in dupes:
            res = any(thisFile in string for string in block)
            if res:
                result = []
                result.append(Path(thisFile).stem[0:lenCheckString])

                for thisPic in block:
                    filename = Path(thisPic).stem
                    filename = filename[0:lenCheckString]
                    res = any(filename in string for string in result)
                    if not res:
                        fileStem = Path(thisPic).stem
                        if fileStem[0:8] == "0000001_":
                            fileStem = fileStem[8:]
                        result.append(fileStem)
                result = list( dict.fromkeys(result) )
                if len(result) > 1:
                    fileCounter += 1
                    counterString = str(fileCounter).zfill(7)
                    newFilename = Path(thisFile).stem + " - " + " - ".join(result) + Path(thisFile).suffix
                    oldFilenameComplete = dirpath + "/" + thisFile
                    newFilenameComplete = "/Users/d045023/bilder/tocheck/" + newFilename
                    print("Renaming file " + newFilenameComplete)
                    #shutil.move(oldFilenameComplete, newFilenameComplete)



