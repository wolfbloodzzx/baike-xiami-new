#!/usr/bin/python
#coding=utf-8

from Spider import spider
from ActorName import ActorNameHelper



if __name__ == "__main__":

    anh = ActorNameHelper("xiami_music_artist.txt")
    id,name = anh.getName()
    while name != None:
        print id+'\t'+name
        crawler = spider()
        crawler.run(name,id)
        id,name = anh.getName()
    anh.close()