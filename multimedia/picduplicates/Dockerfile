FROM python:3.9-buster
ENV HOME_FOLDER /picduplicates
WORKDIR $HOME_FOLDER

#COPY multimedia/picduplicates/requirements.txt /tmp/pip-tmp/
RUN apt-get update
RUN apt-get install -y python3-dev libjpeg-dev gir1.2-gexiv2-0.10 jpeginfo python3-cffi libturbojpeg0-dev python3-gi pkg-config libcairo2-dev gcc python3-dev libgirepository1.0-dev

RUN pip install cffi 
RUN pip install jpegdupes
RUN pip install gobject PyGObject
RUN mkdir -p $HOME_FOLDER/input
