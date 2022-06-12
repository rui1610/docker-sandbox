#!/usr/bin/env bash

docker build -t pidoc .
docker run -itd --name testnode pidoc
docker logs testnode -f
docker kill testnode
docker container rm testnode
docker run -itd -p 127.0.0.1:2222:2222 --name testnode pidoc
docker logs testnode -f
ssh user@password -p 2222