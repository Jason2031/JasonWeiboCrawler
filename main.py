############################################################
#                                                          #
#                     By Jason Wood                        #
#                                                          #
#                wujiecheng@bupt.edu.cn                    #
#                                                          #
############################################################
# encoding: utf-8

import sys
import os

from JasonWeiboCrawler import JasonWeiboCrawler
from JasonWeiboParser import JasonWeiboParser

reload(sys)
sys.setdefaultencoding("utf-8")

if __name__ == '__main__':
    '''
        @description: Main function of the Weibo Crawler
        @:parameter1: User name
        @:parameter2: Password
        @:parameter3: Thread control, "s": single thread, "m": multi thread. (only useful when parameter5 is "u", default "s")
        @:parameter4: Try count, when attempt to download the same page exceeds try count, the thread simply gives up and returns. (default and recommended 20)
        @:parameter5: Multi-thread control, thread interval. (only useful when parameter4 is "m", default 10)
    '''

    if not (2 < len(sys.argv) < 7):
        print '''
        Usage:
            parameter1: User name (login name, must-have)
            parameter2: Password (must-have)
            parameter3: Thread control, "s": single thread, "m": multi thread. (only useful when parameter5 is "u", default "s")
            parameter4: Try count, when attempt to download the same page exceeds try count, the thread simply gives up and returns. (default and recommended 20)
            parameter5: Multi-thread control, thread interval. (only useful when parameter4 is "m", default 10)
        '''
        os._exit(-1)
    else:
        jasonCrawler = 0
        jasonCrawler = JasonWeiboCrawler(sys.argv[1],sys.argv[2])
        if sys.argv[3] is not None:
            if sys.argv[3] == 's':
                try:
                    trycount = int(sys.argv[4])
                except:
                    trycount = 20
                print jasonCrawler.startcrawling(trycount=trycount)
            elif sys.argv[3] == 'm':
                try:
                    trycount = int(sys.argv[4])
                except:
                    trycount = 20
                try:
                    interval = int(sys.argv[5])
                except:
                    interval = 10
                print jasonCrawler.multithreadcrawling(interval=interval, trycount=trycount)
            else:
                print 'Argv3 should be either "s" or "m"'
                os._exit(3)
        else:
            print jasonCrawler.startcrawling(trycount=20)
        jasonParser = JasonWeiboParser(sys.argv[4])
        jasonParser.startparsing()
        jasonParser.save()
        jasonParser.clean()
        print 'Done!'
