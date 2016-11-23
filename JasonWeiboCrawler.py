# coding=utf-8
import os
import requests
from lxml import etree
import threading
import sys
import time
import urllib
import re
import json
import base64

reload(sys)
sys.setdefaultencoding("utf-8")


class JasonWeiboCrawler:
    '''
    This class is used to download weibo text from sina weibo site (weibo.cn).
    Due to the update of the server, some anti-crawling mechanism has been upgraded.
    The old "JasonWeiboCrawler" was blocked by a captcha (http://weibo.cn/interface/f/ttt/captcha/show.php?cpt=2_0a9dacfdff6b94f6).
    Now, four cookie values, specifically "_T_WM", "SUHB", "SUB" and "gsid_CTandWM", are needed.
    In addition, the interested user's uid is needed too.
    If the crawler is used to download weibo texts according to a particular word, or phrase, the uid is not important (but cannot be omitted).
    This class provides two modes to download weibo texts, single-thread and multi-thread.
    '''

    def __init__(self, username, password, wanted):
        self.username = username
        self.password = password
        # self.cook = {"Cookie":self. login()}
        self.cook = self.login()
        self.wanted = wanted

    def login(self):
        self.username = base64.b64encode(self.username.encode('utf-8')).decode('utf-8')
        postData = {
            "entry": "sso",
            "gateway": "1",
            "from": "null",
            "savestate": "30",
            "useticket": "0",
            "pagerefer": "",
            "vsnf": "1",
            "su": self.username,
            "service": "sso",
            "sp": self.password,
            "sr": "1440*900",
            "encoding": "UTF-8",
            "cdult": "3",
            "domain": "sina.com.cn",
            "prelt": "0",
            "returntype": "TEXT",
        }
        loginURL = r'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)'
        session = requests.Session()
        res = session.post(loginURL, data=postData)
        jsonStr = res.content.decode('gbk')
        info = json.loads(jsonStr)
        if info["retcode"] == "0":
            return session.cookies.get_dict()
            # cookies = session.cookies.get_dict()
            # output = ''
            # for key,value in cookies.items():
            #     output+=key + "=" + value+'; '
        else:
            exit(-1)
        output = output.rstrip('; ')
        return output

    def geturl(self, pagenum=1, istest=False):
        url = 'http://weibo.cn/' + self.wanted
        if istest is False:
            url += '/profile'
        if pagenum > 1:
            url = url + '?page=' + str(pagenum)
        return url

    def getpagenum(self, istest=False):
        url = self.geturl(pagenum=1, istest=istest)
        html = requests.get(url, cookies=self.cook).content  # Visit the first page to get the page number.
        selector = etree.HTML(html)
        pagenum = selector.xpath('//input[@name="mp"]/@value')[0]
        return int(pagenum)

    def getpage(self, pageurl):
        return requests.get(pageurl, cookies=self.cook).content

    @staticmethod
    def ispageneeded(html):
        '''
        Sometimes the downloaded html page doesn't any contain useful messages (maybe it's because of the anti-crawling mechanism),
        so it's essential to judge if this page is useful before parsing it.
        :param html: The html text to be judged.
        :return: Returns true if this html is useful.
        '''
        selector = etree.HTML(html)
        try:
            title = selector.xpath('//title')[0]
        except:
            return False
        return title.text != '微博广场' and title.text != '微博'

    @staticmethod
    def savehtml(filepath, html):
        '''
        If the html page is useful, save it to a .txt file.
        :param filepath: The file path that the html page is stored at.
        :param html: Html page text to be stored.
        :return:
        '''
        filehandle = open(filepath, 'w')
        filehandle.write(html)
        filehandle.close()

    def keywordcrawling(self, keyword):
        '''
        Directly download weibo texts that the given keyword appears and parse them.
        :param keyword: Interested keyword.
        :return:
        '''
        realkeyword = urllib.quote(keyword)  # Handle the keyword in Chinese.
        try:
            os.makedirs(sys.path[0] + '/keywords')
        except Exception, e:
            print str(e)
        weibos = []
        try:
            highpoints = re.compile(u'[\U00010000-\U0010ffff]')  # Handle emoji, but it seems doesn't work.
        except re.error:
            highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
        pagenum = 0
        isneeded = False
        while not isneeded:
            html = self.getpage('http://weibo.cn/search/mblog?keyword=%s&page=1' % realkeyword)
            isneeded = self.ispageneeded(html)
            if isneeded:
                selector = etree.HTML(html)
                try:
                    pagenum = int(selector.xpath('//input[@name="mp"]/@value')[0])
                except:
                    pagenum = 1
        for i in range(1, pagenum + 1):
            try:
                isneeded = False
                while not isneeded:
                    html = self.getpage('http://weibo.cn/search/mblog?keyword=%s&page=%s' % (realkeyword, str(i)))
                    isneeded = self.ispageneeded(html)
                selector = etree.HTML(html)
                weiboitems = selector.xpath('//div[@class="c"][@id]')
                for item in weiboitems:
                    cmt = item.xpath('./div/span[@class="cmt"]')
                    if (len(cmt)) == 0:
                        ctt = item.xpath('./div/span[@class="ctt"]')[0]
                        if ctt.text is not None:
                            text = etree.tostring(ctt, method='text', encoding="unicode")
                            tail = ctt.tail
                            if text.endswith(tail):
                                index = -len(tail)
                                text = text[1:index]
                            text = highpoints.sub(u'\u25FD', text)  # Emoji handling, seems doesn't work.
                            weibotext = text
                            weibos.append(weibotext)
                print str(i) + '/' + str(pagenum)
            except Exception, e:
                print str(e)
        f = open(sys.path[0] + '/keywords/' + keyword + '.txt', 'w')
        try:
            f.write(json.dumps(weibos, indent=4, ensure_ascii=False))
        except Exception, ex:
            print str(ex)
        finally:
            f.close()

    def startcrawling(self, startpage=1, trycount=20, istest=False):
        '''
        Single-thread downloading weibo texts.
        :param startpage: Usually omitted
        :param trycount: When attempt to download the same page exceeds trycount, the program simply gives up.
        :return: Returns fasle when the program gives up, otherwise, true.
        '''
        attempt = 0
        try:
            os.makedirs(sys.path[0] + '/Weibo_raw/' + self.wanted)
        except Exception, e:
            print str(e)
        isdone = False
        while not isdone and attempt < trycount:
            try:
                pagenum = self.getpagenum(istest=istest)
                isdone = True
            except Exception, e:
                attempt += 1
            if attempt == trycount:
                return False
        i = startpage
        while i <= pagenum:
            attempt = 0
            isneeded = False
            html = ''
            while not isneeded and attempt < trycount:
                html = self.getpage(self.geturl(i))
                isneeded = self.ispageneeded(html)
                if not isneeded:
                    attempt += 1
                if attempt == trycount:
                    return False
            self.savehtml(sys.path[0] + '/Weibo_raw/' + self.wanted + '/' + str(i) + '.txt', html)
            print str(i) + '/' + str(pagenum)
            i += 1
        return True

    def threadcrawling(self, startpage, endpage, totalpagenum, trycount=20, istest=False):
        '''
        Just don't use this method directly.
        :param startpage:
        :param endpage:
        :param totalpagenum:
        :param trycount:
        :return:
        '''
        i = startpage
        while i <= endpage:
            attempt = 0
            isneeded = False
            html = ''
            while not isneeded and attempt < trycount:  # Give up when attempt to download same page exceeds the threshold.
                html = self.getpage(self.geturl(i, istest=istest))
                isneeded = self.ispageneeded(html)
                if not isneeded:
                    attempt += 1
                if attempt == trycount:
                    if self.lock.acquire():
                        self.result = False
                        self.lock.release()
                        return False
            self.savehtml(sys.path[0] + '/Weibo_raw/' + self.wanted + '/' + str(i) + '.txt', html)
            print str(i) + '/' + str(totalpagenum)
            i += 1
        if self.lock.acquire():
            self.result = self.result & True
            self.lock.release()
        return True

    def multithreadcrawling(self, interval=10, trycount=20, istest=False):
        '''
        Multi-thread downloading weibo texts.
        :param interval: Thread interval, the page number every thread downloads.
        :param trycount: When attempt to download the same page exceeds trycount, the thread simply gives up.
        :return: Returns fasle when any thread gives up, otherwise, true.
        '''
        attempt = 0
        try:
            os.makedirs(sys.path[0] + '/Weibo_raw/' + self.wanted)
        except Exception, e:
            print str(e)
        isdone = False
        self.result = True
        self.lock = threading.Lock()
        while not isdone and attempt < trycount:
            try:
                pagenum = self.getpagenum(istest=istest)
                isdone = True
            except Exception, e:
                attempt += 1
            if attempt == trycount:
                return False
        tasks = []
        threads = pagenum / interval
        for i in range(0, threads):
            t = threading.Thread(target=self.threadcrawling,
                                 args=(i * interval, (i + 1) * interval - 1, pagenum, trycount, istest))
            tasks.append(t)
            t.start()
        t = threading.Thread(target=self.threadcrawling,
                             args=(pagenum - pagenum % interval, pagenum, pagenum, trycount, istest))
        tasks.append(t)
        t.start()
        for t in tasks:
            t.join()
        return self.result
