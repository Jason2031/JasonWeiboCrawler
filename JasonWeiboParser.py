# coding=utf-8
import datetime
import json
import os
import re
import sys

from lxml import etree

from Weibo import Weibo

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

reload(sys)
sys.setdefaultencoding("utf-8")


# this function is used to uniqfy the list, see: http://www.peterbe.com/plog/uniqifiers-benchmark
def f5(seq, idfun=None):
    # order preserving
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        # in old Python versions:
        # if seen.has_key(marker)
        # but in new ones:
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result


def deletefilesorfolders(src):
    '''
    delete files or folders
    '''
    if os.path.isfile(src):
        try:
            os.remove(src)
        except:
            pass
    elif os.path.isdir(src):
        for item in os.listdir(src):
            itemsrc = os.path.join(src, item)
            deletefilesorfolders(itemsrc)
        try:
            os.rmdir(src)
        except:
            pass


class JasonWeiboParser:
    '''
    This class is used to extract weibo texts from plain html page texts stored in file system.
    The extracted weibo are stored in json form in /Weibo_parsed/(uid).txt.
    '''

    def __init__(self, uid):
        self.uid = uid
        self.weibos = []

    def startparsing(self, parsingtime=datetime.datetime.now()):
        basepath = sys.path[0] + '/Weibo_raw/' + self.uid
        for filename in os.listdir(basepath):
            if filename.startswith('.'):
                continue
            path = basepath + '/' + filename
            f = open(path, 'r')
            html = f.read()
            selector = etree.HTML(html)
            weiboitems = selector.xpath('//div[@class="c"][@id]')
            for item in weiboitems:
                try:
                    weibo = Weibo()
                    weibo.id = item.xpath('./@id')[0]
                    cmt = item.xpath('./div/span[@class="cmt"]')
                    if len(cmt) != 0:
                        weibo.isrepost = True
                        weibo.content = cmt[0].text
                    else:
                        weibo.isrepost = False
                    ctt = item.xpath('./div/span[@class="ctt"]')[0]
                    if ctt.text is not None:
                        weibo.content += ctt.text
                    for tag in ctt.xpath('./*'):
                        if tag.tag == 'br' and tag.tail is not None:
                            weibo.content += tag.tail + ' '
                        elif tag.tag == 'a':
                            if tag.text is not None:
                                weibo.content += tag.text
                            if tag.tail is not None:
                                weibo.content += tag.tail
                    if len(cmt) != 0:
                        reason = cmt[1].text.split(u'\xa0')
                        if len(reason) != 1:
                            weibo.repostreason = reason[0]
                    ct = item.xpath('./div/span[@class="ct"]')[0]
                    time = ct.text.split(u'\xa0')[0]
                    weibo.time = self.gettime(self, time, parsingtime).split('.')[0]
                    self.weibos.append(weibo.__dict__)
                except:
                    continue
            f.close()

    @staticmethod
    def gettime(self, timestr, parsingtime):
        timeregex = '\d{1,4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}'
        pattern = re.compile(timeregex)
        match = pattern.search(timestr)
        if match is not None:
            return match.group(0)

        timeregex = u'\d{1,2}月\d{1,2}日 \d{1,2}:\d{1,2}'
        pattern = re.compile(timeregex)
        match = pattern.search(timestr)
        if match is not None:
            month = match.group(0).split('月')[0]
            day = match.group(0).split('日')[0].split('月')[1]
            time = match.group(0).split(' ')[1]
            return str(parsingtime.year) + '-' + month + '-' + day + ' ' + time + ':00'

        timeregex = '\d{0,2}:\d{0,2}'
        pattern = re.compile(timeregex)
        match = pattern.search(timestr)
        if match is not None:
            return str(parsingtime.year) + '-' + str(parsingtime.month) + '-' + str(parsingtime.day) + ' ' + \
                   match.group(0) + ':00'

        timeregex = u'\d{1,2}分钟前'
        pattern = re.compile(timeregex)
        match = pattern.search(timestr)
        if match is not None:
            num = match.group(0).split('分')[0]
            return str(parsingtime - datetime.timedelta(minutes=int(num)))

    def save(self):
        self.weibos = f5(self.weibos, lambda weibo: weibo['id'])
        self.weibos.sort(key=lambda weibo: datetime.datetime.strptime(weibo['time'], '%Y-%m-%d %H:%M:%S'), reverse=True)
        try:
            os.makedirs(sys.path[0] + '/Weibo_parsed/')
        except OSError:
            pass
        f = open(sys.path[0] + '/Weibo_parsed/' + self.uid + '.txt', 'w')
        jsonstr = json.dumps(self.weibos, indent=4, ensure_ascii=False)
        f.write(jsonstr)
        f.close()

    def clean(self):
        '''
        delete the raw files and folder
        '''
        src = sys.path[0] + '/Weibo_raw/' + self.uid
        deletefilesorfolders(src)


if __name__ == '__main__':
    parser = JasonWeiboParser('dummy');
    parser.startparsing()
    parser.save()
