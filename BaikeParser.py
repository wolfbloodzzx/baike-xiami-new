#!/usr/bin/python
#coding=utf-8

from bs4 import BeautifulSoup
import re
import urllib2
import urllib
from download.downloader import HttpDownloader

class baike:

    def __init__(self,html):
        self.soup = BeautifulSoup(html,"lxml")
        pass

    # 删除回车
    def _delret(self,s):
        pat = re.compile('[\r\n]')
        return pat.sub('',s)


    # 抓取表格
    def _parseTable(self,tag):
        data = {}
        data["type"] = "table"
        data["data"] = []
        if tag.find(class_="lemma-album") != None or tag.find(class_="lemma-picture") != None:
            return None
        for tr in tag.find_all("tr"):
            if "class" in tr.attrs.keys() and "cellModule-pager" in tr.attrs["class"]:
                continue
            node = []
            if tr.find("td") != None:
                if tr.find('li') == None:
                    if len(tr.select("td[class~=title-td]")) != 0:
                        node.append("th")
                    else:
                        node.append("td")
                    for td in tr.find_all("td"):
                        node.append(self._delret(td.text))
                    data["data"].append(node)
                else:
                    for l in tr.select("li[class~=row]"):
                        data["data"].append(["td",self._delret(l.text)])
            elif tr.find("th") != None:
                if tr.find('li') == None:
                    node.append("th")
                    for th in tr.find_all("th"):
                        node.append(self._delret(th.text))
                    data["data"].append(node)
        return data

    # 抓取电影电视div
    def parseMovieAndTv(self,tag=None):
        if tag == None:
            tag = self.soup.find(class_="starMovieAndTvplay")
            if tag == None:
                return {}
        if "class" in tag.attrs.keys() and "starMovieAndTvplay" in tag.attrs["class"]:
            data = {}
            data["type"] = "starMovieAndTvplay"
            data["data"] = []

            for li in tag.find_all('li',class_="listItem"):
                m = {}
                if li.find('b',class_="title").find('a') == None:
                    continue
                title_tag = li.select('b[class~="title"] a')
                if len(title_tag) > 0:
                    m["title"] = self._delret(title_tag.text)
                    if 'href' in title_tag.attrs:
                        m["url"] =  title_tag.attrs["href"]
                        if not re.compile("http://").match(m["url"]):
                            m["url"] = "http://baike.baidu.com/"+m["url"]
                    data["data"].append(m)
            return data
        else:
            return {}

    # 抓取音乐div
    def parseMusic(self,tag=None):
        if tag == None:
            tag = self.soup.select("div.module-music.j-common-module")
            if len(tag) > 0:
                tag = tag[0]
            else:
                return {}
        if "class" in tag.attrs.keys() and "module-music" in tag.attrs["class"]:

            data = {}
            data["type"] = "music"

            if tag.find('div',class_="musicHot-wrapper") != None:
                data["musicHot"] = []
                for musicblock in tag.select('div.musicHot-wrapper .musicHot-bloc'):
                    for music in musicblock.find_all('td',class_="item_name"):
                        data["musicHot"].append(self._delret(music.text))

            if tag.find('div',class_="musicAlbumStar-viewport") != None:
                data["musicAlbum"] = []
                for album in tag.select('div.musicAlbumStar-viewport li.album-item .albumName'):
                    node = {}
                    node["title"] = self._delret(album.text)
                    if album.name == "a":
                        node["url"] = album.attrs['href']
                        if not re.compile("http://").match(node["url"]):
                            node["url"] = "http://baike.baidu.com/" + node["url"]
                    data["musicAlbum"].append(node)

            if tag.find('div',class_="musicSingle-wrapper") != None:
                data["musicSingle"] = []
                for tr in tag.select('div.musicSingle-wrapper tr'):
                    node = {}
                    title_tag = tr.select('td .title')
                    year_tag = tr.select('td.align-center')
                    if len(title_tag) == 0 or len(year_tag) == 0:
                        continue
                    node["title"] = self._delret(title_tag[0].text)
                    node["year"] = self._delret(year_tag[0].text)
                    if title_tag[0].find('a') != None:
                        node["url"] = title_tag[0].find('a').attrs['href']
                        if not re.compile("http://").match(node['url']):
                            node["url"] = "http://baike.baidu.com/" + node['url']
                    data["musicSingle"].append(node)

            if tag.find('div',class_="musicOther-wrapper") != None:
                data["musicOther"] = []
                for tr in tag.select('div.musicOther-wrapper tr'):
                    node = {}
                    title_tag = tr.find(class_="title")
                    td = tr.find_all('td')
                    if len(td) < 4 or title_tag == None:
                        continue
                    node['title'] = [self._delret(title_tag.text)]
                    node["singer"] = [self._delret(td[1].text)]
                    node["album"] = [self._delret(td[2].text)]
                    node["time"] = self._delret(td[3].text)
                    if title_tag.find('a')!=None:
                        node['title'].append(title_tag.find('a').attrs['href'])
                    if 'href' in td[1].attrs.keys():
                        node["singer"].append(td[1].attrs["href"])
                    if 'href' in td[2].attrs.keys():
                        node["album"].append(td[2].attrs["href"])

                    data["musicOther"].append(node)
            return data
        else:
            return {}

    # 抓取二三级目录
    def parseLevel(self,tag):
        if tag == None:
            return '',[]
        def get_next_tag(next_tag):
            tag = next_tag.next_sibling
            while tag == '\n':
                tag = tag.next_sibling
            return tag
        next_tag = get_next_tag(tag)
        content = ""
        data = []
        while True:
            if next_tag == None or "class" not in next_tag.attrs.keys():
                break
            if type(next_tag) != type(tag):
                next_tag = get_next_tag(next_tag)
                continue

            if "anchor-list" in next_tag.attrs["class"]:
                next_tag = get_next_tag(next_tag)
                if len(next_tag.find_all('a')) > 1:
                    if "class" not in next_tag.attrs.keys() or "module-music" not in next_tag.attrs["class"]:
                        break
                continue

            if "para" in next_tag.attrs["class"]:
                contents = next_tag.contents
                for i in contents:
                    if type(i) == type(next_tag):
                        if len(i.select('.lemma-picture,.lemma-album')) != 0 or\
                            ("class" in i.attrs.keys() and \
                                     ("lemma-album" in i.attrs["class"] or "lemma-album" in i.attrs["class"])):
                             continue
                        else:
                            content += self._delret(i.text)
                    else:
                        content += self._delret(i)
            elif next_tag.name == "table":
                data.append(self._parseTable(next_tag))
            elif "starMovieAndTvplay" in next_tag.attrs["class"]:
                data.append(self.parseMovieAndTv(next_tag))
            elif "module-music" in next_tag.attrs["class"]:
                data.append(self.parseMusic(next_tag))
            next_tag = get_next_tag(next_tag)
        return content,data

    # 抓取词条简介
    def getDescription(self):

        desc = ''
        desc_tag = self.soup.select('div.feature_poster .desc')
        if len(desc_tag) != 0:
            desc_tag = desc_tag[0]
            for i in desc_tag.find_all(class_="para"):
                desc += self._delret(i.text)+'\n'

        # 存在feature和after块
        elif self.soup.find('div',class_="after-feature-poster") != None:
            # 抓取词条简介
            for i in self.soup.select('.main-content .lemma-summary .para'):
                desc += self._delret(i.text.strip())+'\n'
        # 两块都不存在
        elif len(self.soup.select('div.feature_poster,div.feature-poster')) == 0:
            for i in self.soup.select('.main-content .lemma-summary .para'):
                desc += self._delret(i.text.strip())+'\n'

        return desc

    # 抓取基本信息 baseicnfo 列表模块
    def getBacicInfo(self):
        basic_tag = self.soup.find('div',class_="basic-info cmn-clearfix")
        basicinfo = {}
        if basic_tag != None:
            # basicinfo 中往往分为两列
            for col in basic_tag.find_all("dl"):
                for dt in col.find_all('dt'):
                    dd = dt.next_sibling
                    while dd.name != "dd":
                        dd = dd.next_sibling
                    key = re.compile(u'    ').sub('',dt.text.strip())
                    value = ''
                    # 判断dd是否存在展开内容
                    if dd.find("basicInfo-overlap") != None:
                        value = dd.find("basicInfo-overlap").find("basicInfo-item value").text.strip()
                    else:
                        value = dd.text.strip()
                    basicinfo[key] = value
        return basicinfo

    # 抓取明星关系
    def getRealation(self):
        relation = []
        if self.soup.find(class_="star-info-block relations") != None:
            for node in self.soup.find(id="slider_relations").find_all("li"):
                i = node.find("div",class_="name").contents
                temp_relation = {}
                temp_relation["relation"] = i[0]
                temp_relation["name"] = i[1].text
                temp_relation["url"] = node.find('a').attrs["href"]
                if not re.compile("http://").match(temp_relation["url"]):
                    temp_relation["url"] = "http://baike.baidu.com/"+temp_relation["url"]
                relation.append(temp_relation)
        return relation

    def getMainContent(self):
        maincontent = []

        catelog_class = self.soup.find("div",class_="catalog-list")
        if catelog_class != None:
            catelog = catelog_class.find_all("li")
            if len(catelog) > 0:

                index_l1 = -1
                for cate in catelog:
                    if "level1" in cate.attrs["class"]:
                        node1 = {}
                        node1["name"] = self._delret(cate.find(class_="text").text)
                        node1["content"] = ""
                        node1["data"] = []
                        node1["children"] = []
                        maincontent.append(node1)
                        index_l1 += 1
                    elif "level2" in cate.attrs["class"]:
                        if index_l1 == -1:
                            break
                        node2 = {}
                        node2["name"] = self._delret(cate.find(class_="text").text)
                        node2["content"] = ""
                        node2["data"] = []
                        maincontent[index_l1]["children"].append(node2)

            index_l2 = 0

            anchor_list = self.soup.find_all('div',class_="anchor-list")
            for l2 in maincontent:
                class_name = str(index_l2+1)
                tag = self.soup
                for i in anchor_list:
                    if "name" in i.find('a').attrs.keys() and class_name == i.find('a').attrs["name"]:
                        tag = i
                        break
                if tag == self.soup :
                    continue
                l2["content"],l2["data"] = self.parseLevel(tag)

                # 抓取三级目录
                index_l3 = 0
                if len(l2["children"]) > 0:
                    for l3 in l2["children"]:
                        class_name = str(index_l2+1) + "_" + str(index_l3+1)
                        tag = self.soup
                        for i in anchor_list:
                            if "name" in i.find('a').attrs.keys() and class_name == i.find('a').attrs["name"]:
                                tag = i
                                break
                        if tag == self.soup :
                            continue
                        l3["content"],l3["data"] = self.parseLevel(tag)

                        index_l3 += 1

                index_l2 += 1
        return maincontent

    def parseAllPerson(self):

        head = self.soup.find('ul',class_="polysemantList-wrapper cmn-clearfix")

        result_list = []

        if head != None:
            if head.find('li') != None:
                result_list.append({'title':self._delret(head.find('li').text),'url':''})

            for a_tag in head.select('li.item a'):
                url = a_tag.attrs['href']
                if not re.compile("http://").match(url):
                    url = "http://baike.baidu.com"+url
                result_list.append({'title':self._delret(a_tag.text),'url':url})

        return result_list

    def getCiTiao(self):
        return self._delret(self.soup.find(class_="lemmaWgt-lemmaTitle-title").h1.text)

class searchBaike:

    @staticmethod
    def search(name):
        url = "http://baike.baidu.com/search?word=" + urllib.quote(name) + "&pn=0&rn=0&enc=utf8"
        html = HttpDownloader.download(url)
        soup = BeautifulSoup(html,"lxml")
        if soup.find(class_="no-result") == None:
            if soup.find(class_="create-entrance") == None:
                result_url = soup.find(class_="searchResult").find("dl",class_="search-list").find("dd").find('a').attrs["href"]
                return result_url
        return ""

if __name__ == "__main__":
    searchBaike.search("S.H.E")