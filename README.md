[![Build docker image mp3tool](https://github.com/rui1610/docker-sandbox/actions/workflows/mp3tool.yml/badge.svg)](https://github.com/rui1610/docker-sandbox/actions/workflows/mp3tool.yml) [![Build docker image picturetool](https://github.com/rui1610/docker-sandbox/actions/workflows/picturetool.yml/badge.svg)](https://github.com/rui1610/docker-sandbox/actions/workflows/picturetool.yml)

# docker-sandbox

Various tools to experiment with docker.

## mp3tool

Adds several metadata to mp3 files. 

Mount your local folder with the mp3 files you want to convert and map it to the image folder `/mp3tool/input`.
Do the same for the target folder on your local storage with the image folder `/mp3tool/output`.

When starting the container the tool will start it's work immediately and all the files will be moved to the folder `/mp3tool/output` with their corresponding metadata. Files that are recognized are stored in the `ready` folder within the `/mp3tool/output` folder. Files that were not recognized are moved to the folder  `noCoverImageFound`.

## picturetool

TBD
