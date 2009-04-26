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
from dot.dictmanager import EnglishStopWords
from django.core.cache import cache
#import nltk
searcher = Searcher()
PAGE_SIZE = 20
STOP_WORDS = [u'a', u'an', u'and', u'are', u'as', u'at', u'be', u'but', u'by', u'for', u'if', u'in', u'into', 
          u'is', u'it', u'no', u'not', u'of', u'on', u'or', u'such', u'that', u'the', u'their', u'then',
          u'there', u'these', u'they', u'this', u'to', u'was', u'will', u'with',
          u'you',u'your',u'we',u'he',u'him',u'how',u'where',u'what',u'from',
          # add by myself
          # 的这个词应不应该作为stop word呢
          u'i',u'been',u'about',u'的',u'么',u'是',u'个',u'不',u'们',u'这',u'那',u'我',u'你',u'很',u'了',u'以',u'与',u'为',u'一']
STOP_WORDS = EnglishStopWords().dict
STOP_WORDS.extend([u'的',u'么',u'是',u'个',u'不',u'们',u'这',u'那',u'我',u'你',u'很',u'了',u'以',u'与',u'为',u'一'])
mapper = matrixmapper.MatrixMapper(STOP_WORDS)
def query(query, page,category_what,data_size=200,nobuildcategory=False):
    category_id = None
    if category_what:
        category_ = dao.Category.objects.filter(what=category_what)[0]
        category_id = category_.id
    
    
    hits = searcher.search(query,category_id)
    
    doc_ids = []
    for i in range(len(hits)):
        doc_ids.append(hits.id(i))
    #这里将空格替换为+号，否则会报错，对应地在catfilter中从cache中值时也要将query的空格替换为+号
    cache.add(query.replace(' ','+'),doc_ids,3600)
    #相关类目,暂不使用
    #cats = dao.get_keywords(query)
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
            entry.summary = entry.summary[0:data_size] + "..."
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
                
    dispCats = dao.QueryCategoryDisp.objects.filter(query__keyword=query) 
    label = []
    if dispCats:
        for cat in dispCats:
            qec=dao.QueryEntryCategory.objects.filter(query__keyword=query,category=cat.category)
            label.append([cat.weight,cat.category.what,len(qec)])
        label.sort(reverse=True)
    phrases,label_doc = (dispCats and {},[]) or discover_freq_phrases(docs,query)
    
    #for i in range(len(docs)):
        #raw_cat = results[i].category.what
        #if raw_cat == u'其他' and phrases[i].label_weight:
         #   results[i].category.what = phrases[i].text
            
    return results, scores,total,phrases,dispCats and label[:10] or label_doc[:10]

def discover_freq_phrases(docs,query):
    print 'sfds'
    doc_label,label_doc = mapper.build(docs,query)
    return doc_label,label_doc