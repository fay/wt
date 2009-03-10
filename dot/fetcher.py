# -*- coding: utf-8 -*-
from urllib import urlopen
from textwrap import wrap
from dot.feedlist import feeds_url
from dot import feedparser
from apps.wantown.models import Feed, Entry, Category
from apps.wantown import dao
import datetime,time
from HTMLParser import HTMLParser
from dot import feedlist
from dot import googleclient
def strip_tags(html):
    html = html.strip()
    html = html.strip("\n")
    result = []
    parser = HTMLParser()
    parser.handle_data = result.append
    parser.feed(html)
    parser.close()
    return ''.join(result)

def fetch(url,is_write=True):
    print 'parsing: ',url
    if not url:
        return
    if Feed.objects.filter(rss_link=url):
        return 'pass'
    try:
        soup = feedparser.parse(url) 
    except Exception,e:
        print 'parsing error',e
        return  
     
    feed_link = soup.feed.get('link','')
    feed = dao.get_by_link(feed_link, Feed)
    if not feed:
        feed = Feed(link=feed_link)
    feed.title = soup.feed.get('title','')
    if Feed.objects.filter(title=feed.title):
        return 'pass'
    feed.description = soup.feed.get('description','')
    feed.rss_link = url
    dao.save_model(feed)
    if not soup['entries']:
        print 'this feed has not entries'
        return
    if is_write:
        fetch_entries(feed,soup['entries'])

def fetch_entries(feed,entries):

    for entry in entries:
        entry_link = entry['link']  
        entry_model = dao.get_by_link(entry_link, Entry)
        if not entry_model:
            entry_model = Entry(feed=feed, link=entry_link)
        else:
            continue
        entry_model.title = entry['title']
        if len(entry_model.title) >= 200:
            continue
        entry_model.author = entry.get('author', 'unknow')
        entry_model.summary = entry.get('summary', '')
        if not entry_model.summary:
            content = entry.get('content', '')
            try:
                entry_model.summary = (type(content) == unicode and content) or content[0].get('value', '')
            except:
                continue
        #clear html tags
        entry_model.summary = strip_tags(entry_model.summary)
        if len(entry_model.summary) <= 100:
            return 
        entry_model.when = entry.get('updated_parsed','') or time.localtime(entry.get('updated'))
        if entry_model.when:
            entry_model.when = datetime.datetime(entry_model.when[0],entry_model.when[1],entry_model.when[2],entry_model.when[3],entry_model.when[4])
        tags = None
        if entry.has_key('tags'):
            tags = entry.get('tags', '')
            tags = tags[0].get('term','')
        if not tags and entry.has_key('categories'):
            tags = entry.get('categories')
            tags = tags.values()[0]
        if not tags:
            print 'no tags.ignored...'
            continue
        else:
            cat = dao.save_category(tags)
            entry_model.category = cat
        try:
            dao.save_model(entry_model)
        except Exception,e:
            print 'save error:',e
        
def update_local():
    for feed in Feed.objects.all():
        try:
            soup = feedparser.parse(feed.rss_link) 
        except Exception,e:
            print 'parsing error',e
            continue
        fetch_entries(feed,soup['entries'])
        
def update_from_google_reader():
    reader = googleclient.get_reader()
    feed_list = reader.get_subscription_list()['subscriptions']
    for f in feed_list:
        link = f['id'].encode('utf-8')
        print link
        fetch_from_google_reader(reader,link)
        
def fetch_from_google_reader(reader,link,count=20):
    try:
        google_feed = reader.get_feed(feed=link,count=count)
    except Exception,e:
        print 'error:',e
        return
    if not google_feed:
        return
    #得到feed原始地址
    feed_link = google_feed._properties['link'].getAttribute('href').encode('utf-8')
    feed = dao.get_by_link(feed_link, Feed)
    if not feed:
        feed = Feed(link=feed_link)
    feed.title = google_feed.get_title().encode('utf-8')
    feed.description = google_feed._properties.get('description','').encode('utf-8')
    #删除前缀'feed/'
    feed.rss_link = link[5:]
    dao.save_model(feed)
    fetch_entries(feed ,google_feed.get_entries())