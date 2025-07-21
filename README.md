#to init
docker build -t my-python3:latest. 


docker run --rm -it -v /home/jbrauxxx/Documents/crawling:/home/jbrauxxx/Documents/crawling python:latest bash

#to run/debug/etc
docker run --rm -it -v /home/jbrauxxx/Documents/crawling:/home/jbrauxxx/Documents/crawling my-python3:latest bash 

