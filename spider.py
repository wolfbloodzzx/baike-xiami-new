#!/usr/bin/python
#coding=utf-8

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import threading
from BaikeParser import searchBaike
from download.downloader import HttpDownloader
from BaikeParser import baike
from FileSaver import saver
import BaikeLogger
from download.downloader import HttpDownloader
import json


class spider(threading.Thread):

    def __init__(self,url):
        pass

    def _getData(self,b,url,tag=''):
        data = {}
        data["basicinfo"] = b.getBacicInfo()
        data["description"] = b.getDescription()
        data["relationship"] = b.getRealation()
        data["maintain"] = b.getMainContent()
        data["url"] = url
        data["tag"] = tag
        return data

    def run(self,name):
        url = searchBaike.search(name)
        if url != '':
            result = []
            b = baike(HttpDownloader.download(url))
            person_list = b.parseAllPerson()
            if len(person_list) == 0:
                result.append(self.getData(b,url))
            else:
                flag = 0
                for i in person_list:
                    if flag == 0:
                        self._getJsonData(b,url,i["title"])
                        flag = 1
                    t_b = baike(HttpDownloader.download(i['url']))
                    result.append(self._getData(t_b,i['url'],i['title']))

            jstr = json.dumps(result,ensure_ascii=False)
            saver_handle = saver('out_data_json.txt')
            saver_handle.write(jstr)
            saver_handle.close()

        pass

    def __stop(self):
        pass