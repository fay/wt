# -*- coding: utf-8 -*-
from apps.wantown.models import Object, Feed, Category, Entry, Clone, Query, QueryCategory, QueryEntryCategory,QueryCategoryDisp
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import Q


#保存一个Object对象，返回的是Key对象
def save(who, what, which, category, available='no'):
    object = Object(who=who, what=what, which=which, available=available, category=category)
    object.save()
    return object.id

def list(size=10):
    return Object.objects.all().order_by("-when")

def get(id):
    return Object.objects.get(id=id)
    
def save_category(what, weight=0, type='d'):
    exist_category_query = Category.objects.filter(what=what)
    exist_category = None
    if exist_category_query:
        exist_category = exist_category_query.get()
        if weight != 0:
            exist_category.weight = (exist_category.weight + weight) / 2
        exist_category.save()
    if not exist_category:
        category = Category(what=what, weight=weight, type=type)
        category.save()
        return category
    else:
        return exist_category
#QueryEntryCategory是唯一的
def save_entry_cat(query, entry, cat, weight=0):
    ec_query = QueryEntryCategory.objects.filter(query=query, entry=entry, category=cat)
    if ec_query:
        ec = ec_query.get()
        ec.weight = (ec.weight + weight)/2
        ec.save()
    else:
        ec = QueryEntryCategory(query=query, entry=entry, category=cat, weight=weight)
        ec.save()
    return ec
#用户点击的查询词－类目    
def get_keywords(keyword):
    qc = QueryCategory.objects.filter(query__keyword=keyword)
    for i in qc:
        i.count = i.category.weight
    return sorted(qc,reverse=True)
#检查是否存在已有的关键字－类目
def get_keyword_category(keyword, category_id,modelClass=QueryCategory):
    exist_keyword_query = modelClass.objects.filter(query__keyword=keyword, category__id=category_id)
    if exist_keyword_query:
        return exist_keyword_query.get()
    else:
        return None

#通过查询词和类目名查找QueryCategoryDisp对象,看是否存在
def get_keyword_category_by_category(keyword, category):
    exist_keyword_query = QueryCategoryDisp.objects.filter(query__keyword=keyword, category__what=category)
    if exist_keyword_query:
        return exist_keyword_query.get()
    else:
        return None
def distinct_query(keyword):
    query = Query.objects.filter(keyword=keyword)
    if query:
        query = query.get()
    else:
        try:
            query = Query(keyword=keyword, count=1)
            query.save()
        except:
            print 'a'
    return query

def save_qc_with_weight(keyword,weight,category_):
    cat = save_category(category_,weight)
    exist_qc = get_keyword_category(keyword, cat.id,QueryCategoryDisp)
    if not exist_qc:
        query = distinct_query(keyword)            
        keywordModel = QueryCategoryDisp(query=query, category=cat, weight=weight)
        return keywordModel.save()
    else:
        exist_qc.weight = weight
        return exist_qc.save()
    
#保存查询关键字，如果数据库中已经存在则增加计数，否则新建关键字对象且计数
def save_keyword(keyword, category_id):
    exist_keyword = get_keyword_category(keyword, category_id)
    if not exist_keyword:
        query = distinct_query(keyword)
        keywordModel = QueryCategory(query=query, category=Category.objects.get(id=category_id), count=1)
        return keywordModel.save()
    else:
        exist_keyword.count = exist_keyword.count + 1
        return exist_keyword.save()
def save_user(email, password):
    who = User(email=email, password=password)
    return  who.save()

def save_clone(object, who):
    return Clone(object=object, who=who).save()

def query(which, what):
    return Object.objects.filter(which=which)

def save_model(model):
    return model.save()
#通过link查找feed,如果存在则返回它，不存在则创建一个新的feed
def get_by_link(link, ModelClass):
    q = ModelClass.objects.filter(link=link)
    if q:
        try:
            model = q.get()
        except MultipleObjectsReturned, e:
            for i in q[1:]:
                i.delete()
            print e
            return q[0]
        return model
    else:
        return None 

def get_total_feeds():
    return Feed.objects.count()

def get_total_entries():
    return Entry.objects.count()
#根据查询关键字搜索类目
def search_category(keyword):
    return Category.objects.filter(Q(what__icontains=keyword)).distinct()

#弃用,get_category_count_by_entry2取代之
def get_category_count_by_entry(query, entry):
    query = Query.objects.filter(keyword=query)
    
    if query:
        query = query.get()
        print query.id
    qc = QueryCategory.objects.filter(query=query)
    counts = []
    for i in qc:
        print i.category.id
        qec = QueryEntryCategory.objects.filter(query=query, entry=entry, category=i.category)
        if qec:
            counts.append(i.count)
    return float(sum(counts)) / (len(counts) or 1)

#用于索引时加权
def get_category_count_by_entry2(entry):
    qec = QueryEntryCategory.objects.filter(entry=entry)
    counts = []
    for i in qec:
        qc = QueryCategory.objects.filter(query=i.query,category=i.category)
        if qc:
            for j in qc:
                counts.append(j.count)
    return float(sum(counts)) / (len(counts) or 1)

#用于通过查询词和指定的Entry得到该entry的所有类目
#具体地，用于用户点击行为保存点击entry所属的类目
def get_qec_by_qe(keyword,entry_id):
    entry=Entry.objects.get(id=entry_id)
    return QueryEntryCategory.objects.filter(query=Query.objects.filter(keyword=keyword).get(),entry=entry)