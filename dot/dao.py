# -*- coding:utf-8 -*-
import os,string
from dot.searcher import Searcher,STORE_DIR
from dot import cseg,featurex
from dot.ntlk import SimpleTokenizer
from apps.wantown.models import Entry
from apps.wantown import dao
from lucene import Hit,IndexReader
from django.core.paginator import Paginator, InvalidPage, EmptyPage
import nltk
searcher = Searcher()

def query(query, page):
    hits = searcher.search(query)
    query = dao.get_keywords(query)
    results = []
    scores = []
    #last page number
    total = hits.length()
    pages_num = total / 20 + (total % 20 and 1) or 0
    if ((page - 1) * 20) > total :
        page = pages_num
    docs = []
    for i in range(20):
        start = (page - 1) * 20
        if start + i >= total:
            break

        doc = hits.doc(i + start)
        docs.append(doc)
        link = doc.get("link")
        entry = dao.get_by_link(link, Entry)
        if entry:
            entry.summary = entry.summary[0:200] + "..."
            results.append(entry)
            scores.append(hits.score(i + (page - 1) * 20))
        
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
    #ireader = IndexReader.open(STORE_DIR)
    stop = [',','.','*','。','/','-','a','you','and','to','this',u'的']
    #dic = loader.load()
    #dm = featurex.getDictManager()
    entries = []
    tokenizer = SimpleTokenizer()
    fdist = nltk.FreqDist()
    for doc in docs:
            link = doc.get("link")
            entry = dao.get_by_link(link, Entry)
            tokens = tokenizer.tokenize(entry.summary)
            text = nltk.Text(tokens)            
            fdist.inc(text)
    for rank, word in enumerate(fdist):
         tf = 0
    words_dict = featurex.tf_idf(entries, dm.seg_dict)
    m = {}
    for k,v in words_dict.items():
        m[k] = v.feature_value
    items = m.items()
    items.sort(lambda (k1,v1),(k2,v2):cmp(v2,v1))
    items = string.join(map(lambda(x,y):x,items),"\001")
    items = items.split('\001')
    return items[0:10]
    if 0:
        words_dict  = {}
        mix = ''
        for doc in docs:
            link = doc.get("link")
            entry = dao.get_by_link(link, Entry)
            mix += entry.summary + " "
        doc = featurex.Document(mix.encode('utf-8'),dm)
        m = {}
        for k,v in doc.words_dict.items():
            m[k] = v.feature_value
        items = m.items()
        items.sort(lambda (k1,v1),(k2,v2):cmp(v2,v1))
        items = string.join(map(lambda(x,y):x,items),"\001")
        items = items.split('\001')
        return items[0:10]