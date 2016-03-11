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


class spider:

    def __init__(self):
        pass

    def _getData(self,b,url,tag=''):
        data = {}
        data["basicinfo"] = b.getBacicInfo()
        data["description"] = b.getDescription()
        data["relationship"] = b.getRealation()
        data["maintain"] = b.getMainContent()
        data["url"] = url
        data["tag"] = tag
        data["citiao"] = b.getCiTiao()
        return data

    def run(self,name,id):
        try:
            url = searchBaike.search(name)
            if url != '':
                result = []
                b = baike(HttpDownloader.download(url))
                person_list = b.parseAllPerson()
                if len(person_list) == 0:
                    result.append(self._getData(b,url))
                else:
                    flag = 0
                    for i in person_list:
                        if flag == 0:
                            data = self._getData(b,url,i["title"])
                            data['id'] = id
                            result.append(data)
                            flag = 1
                        else:
                            t_b = baike(HttpDownloader.download(i['url']))
                            data = self._getData(t_b,i['url'],i['title'])
                            data['id'] = id
                            result.append(data)

                jstr = json.dumps(result,ensure_ascii=False)
                saver_handle = saver('out_data_json.txt')
                saver_handle.write(jstr+'\n')
                saver_handle.close()
            else:
                saver_handle = saver("star_not_found.txt")
                saver_handle.write(id+'\t'+name+'\n')
                saver_handle.close()
        except AttributeError,e:
            print "AttributeError"
            print e.message
            s = saver("error_list.txt")
            s.write("AttributeError\t"+id+'\t'+name+'\n')
            s.close()
        except IOError,e:
            print "IOError"
            print e.message
            s = saver("error_list.txt")
            s.write("IOError\t"+id+'\t'+name+'\n')
            s.close()

        pass

    def __stop(self):
        pass

if __name__ == "__main__":
    sp = spider()
    sp.run("李宇春",'1')