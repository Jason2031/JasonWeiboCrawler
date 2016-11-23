############################################################
#                                                          #
#                     By Jason Wood                        #
#                                                          #
#                wujiecheng@bupt.edu.cn                    #
#                                                          #
############################################################
# encoding: utf-8

import os
import sys

from JasonWeiboCrawler import JasonWeiboCrawler
from JasonWeiboParser import JasonWeiboParser

reload(sys)
sys.setdefaultencoding("utf-8")

if __name__ == '__main__':
    '''
        @description: Main function of the Weibo Crawler
        @:parameter1: User name (login name, must-have)
        @:parameter2: Password (must-have)
        @:parameter3: Function control, "k": keyword crawling, "u": user's weibos crawling. (must-have)
        @:parameter4: If the 3rd parameter is "k", then this parameter should be the interested keyword, otherwise, interested uid. (must-have)
        @:parameter5: Thread control, "s": single thread, "m": multi thread. (only useful when parameter5 is "u", default "s")
        @:parameter6: This arg is for weibo gathering process, it's purpose is to tell whether this program to run in regular mode or test mode. (must-have, r/t, default r)
        @:parameter7: Try count, when attempt to download the same page exceeds try count, the thread simply gives up and returns. (default and recommended 20)
        @:parameter8: Multi-thread control, thread interval. (only useful when parameter4 is "m", default 10)
    '''

    if not (4 < len(sys.argv) < 10):
        print '''
        Usage:
            parameter1: User name (login name, must-have)
            parameter2: Password (must-have)
            parameter3: Function control, "k": keyword crawling, "u": user's weibos crawling. (must-have)
            parameter4: If the 3rd parameter is "k", then this parameter should be the interested keyword, otherwise, interested uid. (must-have)
            parameter5: Thread control, "s": single thread, "m": multi thread. (only useful when parameter5 is "u", default "s")
            parameter6: This arg is for weibo gathering process, it's purpose is to tell whether this program to run in regular mode or test mode. (must-have, r/t, default r)
            parameter7: Try count, when attempt to download the same page exceeds try count, the thread simply gives up and returns. (default and recommended 20)
            parameter8: Multi-thread control, thread interval. (only useful when parameter4 is "m", default 10)
        '''
        os._exit(-1)
    else:
        jasonCrawler = 0
        if sys.argv[3] == 'k':
            jasonCrawler = JasonWeiboCrawler(sys.argv[1], sys.argv[2], 'dummy')
            jasonCrawler.keywordcrawling(sys.argv[4])
        elif sys.argv[3] == 'u':
            jasonCrawler = JasonWeiboCrawler(sys.argv[1], sys.argv[2], sys.argv[4])
            if sys.argv[5] is not None:
                if sys.argv[5] == 's':
                    try:
                        trycount = int(sys.argv[7])
                    except:
                        trycount = 20
                    if sys.argv[6] == 't':
                        print jasonCrawler.startcrawling(trycount=trycount, istest=True)
                    else:
                        print jasonCrawler.startcrawling(trycount=trycount)
                elif sys.argv[5] == 'm':
                    try:
                        trycount = int(sys.argv[7])
                    except:
                        trycount = 20
                    try:
                        interval = int(sys.argv[8])
                    except:
                        interval = 10
                    if sys.argv[6] == 't':
                        print jasonCrawler.multithreadcrawling(interval=interval, trycount=trycount, istest=True)
                    else:
                        print jasonCrawler.multithreadcrawling(interval=interval, trycount=trycount)
                else:
                    print 'Argv5 should be either "s" or "m"'
                    os._exit(5)
            else:
                print jasonCrawler.startcrawling(trycount=20)
            jasonParser = JasonWeiboParser(sys.argv[4])
            jasonParser.startparsing()
            jasonParser.save()
            jasonParser.clean()
        else:
            print 'Argv4 should be either "k" or "u"'
            os._exit(4)
        print 'Done!'
