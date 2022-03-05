FROM python:3.10-alpine
ENV HOME_FOLDER /mp3metadatafetcher
WORKDIR $HOME_FOLDER

COPY multimedia/mp3metadatafetcher/requirements.txt /tmp/pip-tmp/
COPY multimedia/mp3metadatafetcher/mp3metadatafetcher.py $HOME_FOLDER

RUN  apk add  --no-cache --virtual .tmp gcc libc-dev linux-headers jpeg-dev zlib-dev \
    && pip install --no-cache-dir -r /tmp/pip-tmp/requirements.txt \
    && rm -rf /tmp/pip-tmp \
    && apk del .tmp gcc libc-dev linux-headers jpeg-dev zlib-dev \
    && apk add bash libjpeg\
    && rm -r /tmp/* \
    && rm -rf /var/cache/apk/* \
    && mkdir -p $HOME_FOLDER/media \
    && mkdir -p $HOME_FOLDER/converted 

CMD ["python","mp3metadatafetcher.py"]
