# -*- coding: utf-8 -*-

import urllib2,re
from BeautifulSoup import *
from urlparse import urljoin
from cPickle import Pickler,Unpickler
from apps.wantown.models import Link,Feed
from dot import fetcher
from dot import googleclient
class Crawler(object):
    def __init__(self):
        self.history_file = 'history.txt'
    def addtoDB(self,link,is_crawled='y'):
        Link(link=link,is_crawled=is_crawled).save()
    
    def crawle(self,pages,depth=2):
        reader = googleclient.get_reader()
        for i in range(depth):
            newpages = []
            for page in pages:
                print 'crawling... ',page
                query = Link.objects.filter(link=page)
                if query:
                    #如果已经爬过则pass
                    if query.get().is_crawled == 'y':
                        print page,'already crawled'
                        continue
                try:
                    c=urllib2.urlopen(page)
                except:
                    print "Could not open %s" % page
                    continue
                try:
                    soup=BeautifulSoup(c.read())
                    if query:
                        linkModel = query.get()
                        if linkModel.is_crawled == 'n':
                            linkModel.is_crawled = 'y'
                            linkModel.save()
                    else:
                        self.addtoDB(page, 'y')
                    #找到所有超链接
                    links=soup('a')
                    for link in links:
                        if ('href' in dict(link.attrs)):
                            url=urljoin(page,link['href'])
                            if url.find("'")!=-1: continue
                            url=url.split('#')[0]  # remove location portion
                            match1 = re.match('(http://[\w.]*/)',page)
                            match2 =  re.match('(http://[\w.]*/)',url)
                            if url[0:4]=='http' and not Link.objects.filter(link=url):
                                if match1 and match2 and match1.group() == match2.group():
                                    continue
                                newpages.append(url)
                                print 'appending:',url
                                self.addtoDB(url,'n')
                    rss_links=soup('link')
                    for link in rss_links:
                        if ('type' in dict(link.attrs) and link['type'] == "application/rss+xml"):
                            url=urljoin(page,link['href'])
                            if url.find("'")!=-1: continue
                            if url[0:4]=='http' and not Feed.objects.filter(link=url):
                                ret = fetcher.fetch(url,False)
                                if ret == 'pass':
                                    print url,':already exists'
                                    continue
                                reader.add_subscription(feed='feed/'+url)
                                fetcher.fetch_from_google_reader(reader,'feed/'+url)
                                
                except Exception,e:
                    print e
            pages=newpages
                    
            
