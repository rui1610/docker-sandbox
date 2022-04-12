FROM python:3.10-alpine
ENV HOME_FOLDER /mp3tool
WORKDIR $HOME_FOLDER

COPY multimedia/mp3tool/requirements.txt /tmp/pip-tmp/

# RUN  apk add  --no-cache --virtual .tmp gcc libc-dev linux-headers jpeg-dev zlib-dev \
#     && pip install --no-cache-dir -r /tmp/pip-tmp/requirements.txt \
#     && rm -rf /tmp/pip-tmp \
#     && apk del .tmp gcc libc-dev linux-headers jpeg-dev zlib-dev \
#     && apk add bash libjpeg\
#     && rm -r /tmp/* \
#     && rm -rf /var/cache/apk/* \
#     && mkdir -p $HOME_FOLDER/media \
#     && mkdir -p $HOME_FOLDER/converted \
#     && cp /usr/share/zoneinfo/Europe/Berlin /etc/localtime


RUN  apk add  --no-cache --virtual .tmp  gcc libc-dev linux-headers \
    && pip install --no-cache-dir -r /tmp/pip-tmp/requirements.txt \
    && rm -rf /tmp/pip-tmp \
    && apk del .tmp gcc libc-dev linux-headers \
    && apk add bash \
    && rm -r /tmp/* \
    && rm -rf /var/cache/apk/* \
    && mkdir -p $HOME_FOLDER/media \
    && mkdir -p $HOME_FOLDER/converted \
    && cp /usr/share/zoneinfo/Europe/Berlin /etc/localtime

COPY multimedia/mp3tool/mp3tool.py $HOME_FOLDER
COPY multimedia/mp3tool/helper*.py $HOME_FOLDER/

ENTRYPOINT ["python","mp3tool.py"]
#CMD ["bash"]
