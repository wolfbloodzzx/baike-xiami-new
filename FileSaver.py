#!/usr/bin/python
#coding=utf-8

class saver:

    def __init__(self,filename):
        self.fp = open(filename,'a+')
        pass

    def write(self,text):
        self.fp.write(text)
        pass

    def close(self):
        self.fp.close()
        pass
