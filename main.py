#!/usr/bin/python
#coding=utf-8

from Spider import spider
from ActorName import ActorNameHelper
import sys



if __name__ == "__main__":

    anh = ActorNameHelper("xiami_music_artist.txt")
    ans = 1
    id,name = anh.getName()
    while name != None:
        print str(ans) + ':\t' + id+'\t'+name
        crawler = spider()
        crawler.run(name,id)
        id,name = anh.getName()
        ans += 1
        sys.stdout.flush()
    anh.close()