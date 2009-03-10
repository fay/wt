# -*- coding: utf-8 -*-
from apps.wantown.models import Object, Feed, Category, Entry, Clone, Query
from django.contrib.auth.models import User
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
    
def save_category(what):
    exist_category_query = Category.objects.filter(what=what)
    exist_category = None
    if exist_category_query:
        exist_category = exist_category_query.get()
    if not exist_category:
        category = Category(what=what)
        category.save()
        return category
    else:
        return exist_category
    
def get_keywords(keyword):
    return Query.objects.filter(keyword=keyword).order_by('-count')

#检查是否存在已有的关键字－类目
def get_keyword_category(keyword,category_id):
    exist_keyword_query = Query.objects.filter(keyword=keyword, category__id=category_id)
    if exist_keyword_query:
        return exist_keyword_query.get()
    else:
        return None
#保存查询关键字，如果数据库中已经存在则增加计数，否则新建关键字对象且计数
def save_keyword(keyword, category_id):
    exist_keyword = get_keyword_category(keyword,category_id)
    if not exist_keyword:
        keywordModel = Query(keyword=keyword, category=Category.objects.get(id=category_id), count=1)
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
        return q.get()
    else:
        return None 

def get_total_feeds():
    return Feed.objects.count()

def get_total_entries():
    return Entry.objects.count()
    
#根据查询关键字搜索类目
def search_category(keyword):
    return Category.objects.filter(Q(what__icontains=keyword)).distinct()
