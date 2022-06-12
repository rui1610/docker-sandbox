docker build -t pidoc .
docker run -itd --name testnode pidoc
docker logs testnode -f
