# -*- coding:utf-8 -*-
import os,string
from dot.searcher import Searcher,STORE_DIR
from dot import matrixmapper
#from dot import cseg,featurex
#from dot.ntlk.cseg import SimpleTokenizer
from apps.wantown.models import Entry
from apps.wantown import dao
from lucene import Hit,IndexReader
from django.core.paginator import Paginator, InvalidPage, EmptyPage
#import nltk
searcher = Searcher()
PAGE_SIZE = 20
def query(query, page):
    hits = searcher.search(query)
    query = dao.get_keywords(query)
    results = []
    scores = []
    #last page number
    total = hits.length()
    pages_num = total / PAGE_SIZE + (total % PAGE_SIZE and 1) or 0
    if ((page - 1) * PAGE_SIZE) > total :
        page = pages_num
    docs = []
    for i in range(PAGE_SIZE):
        start = (page - 1) * PAGE_SIZE
        if start + i >= total:
            break

        doc = hits.doc(i + start)
        docs.append(doc)
        link = doc.get("link")
        entry = dao.get_by_link(link, Entry)
        if entry:
            entry.summary = entry.summary[0:200] + "..."
            results.append(entry)
            scores.append(hits.score(i + (page - 1) * PAGE_SIZE))
        
    if 0:
        for hit in hits:
            doc = Hit.cast_(hit).getDocument()
            link = doc.get("link")
            entry = dao.get_by_link(link, Entry)
            if entry:
                entry.summary = entry.summary[0:200] + "..."
                results.append(entry)
                scores.append(Hit.cast_(hit).getScore())
    phrases = discover_freq_phrases(docs)
    return results, scores, query,total,phrases

def discover_freq_phrases(docs):
    STOP_WORDS = [u'a', u'an', u'and', u'are', u'as', u'at', u'be', u'but', u'by', u'for', u'if', u'in', u'into', 
              u'is', u'it', u'no', u'not', u'of', u'on', u'or', u'such', u'that', u'the', u'their', u'then',
              u'there', u'these', u'they', u'this', u'to', u'was', u'will', u'with',
              # add by myself
              u'i',u'been',u'about',u'不',u'们',u'这',u'那',u'的',u'己',u'我',u'你',u'很',u'了',u'以',u'与',u'为',u'一']
    mapper = matrixmapper.MatrixMapper(STOP_WORDS)
    labels = mapper.build(docs)
    return labels