FROM python:3.8-alpine
ENV HOME_FOLDER /picturetool
WORKDIR $HOME_FOLDER

COPY multimedia/picturetool/requirements.txt /tmp/pip-tmp/

RUN apk add --update --no-cache --virtual .tmp \
                gcc  \
                libc-dev  \
                libraw \
                linux-headers \ 
                jpeg-dev  \
                zlib-dev  \
    && pip install -r /tmp/pip-tmp/requirements.txt \
    && rm -rf /tmp/pip-tmp \
    && apk del .tmp gcc libc-dev linux-headers jpeg-dev zlib-dev \
    && apk add bash fdupes exiftool imagemagick ffmpeg\
    && rm -r /tmp/* \
    && rm -rf /var/cache/apk/* \
    && mkdir -p $HOME_FOLDER/source \
    && mkdir -p $HOME_FOLDER/target \
    && mkdir -p $HOME_FOLDER/temp \
    && cp /usr/share/zoneinfo/Europe/Berlin /etc/localtime

COPY multimedia/picturetool/picturetool.py $HOME_FOLDER
COPY multimedia/picturetool/gpstool.py     $HOME_FOLDER

#CMD ["bash"]
