#!/usr/bin/python
#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class ActorNameHelper:
    def __init__(self,file):
        self.fp = open(file,'r')
        pass

    def getName(self):
        line = self.fp.readline()
        if not line:
            return None,None
        line = line.strip()
        l = line.split('\t')
        while line.strip() == '' or len(l) != 2:
            line = self.fp.readlines()
        return l[0],l[1]

    def close(self):
        self.fp.close()

    def getNames(self):
        pass