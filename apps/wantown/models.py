# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.core import signals
from dot.postrequest import save_categories

# Create your models here.
class Category(models.Model):
    what = models.CharField(max_length=100)
    parent_cat = models.ForeignKey('self',null=True,blank=True)
    weight = models.FloatField()
    type = models.CharField(max_length=1,choices=(('d','dynamic'),('s','static')))
    
    def __str__(self):
        return self.__unicode__()
    def __unicode__(self):
        return self.what
class Object(models.Model):
    who = models.ForeignKey(User,null=True)
    what = models.CharField(max_length=200)
    which = models.CharField(max_length=4,choices=(('want','want'),('own', 'own')))
    when = models.DateTimeField(auto_now=True)
    available = models.CharField(max_length=3,choices=(('yes','yes'),('yes', 'no')))
    category = models.ForeignKey(Category)
    
    def __str__(self):
        return self.__unicode__()
    def __unicode__(self):
        return "%s %s a(n) %s" % (self.who, self.which, self.what)
    


#用于用户对已有的Object的复制，在具体业务中称为'我也想要'    
class Clone(models.Model):
    who = models.ForeignKey(User)
    object = models.ForeignKey(Object)
    
class Feed(models.Model):
    title = models.CharField(max_length=200)
    link = models.URLField()
    rss_link = models.URLField()
    description = models.TextField()
    
class Entry(models.Model):
    feed = models.ForeignKey(Feed)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    summary = models.TextField()
    link = models.URLField()
    when = models.DateTimeField()
    category = models.ForeignKey(Category)
    

    def __unicode__(self):
        return '%s %s %s %s %s %s' % (self.title,self.author,self.summary,self.link,self.when,self.category)
    #kind = models.CharField(max_length=1,choices=(('w','want'),('o', 'own')))


class Query(models.Model):
    keyword = models.CharField(max_length=200)
    count = models.IntegerField()
    
class QueryEntryCategory(models.Model):
    query = models.ForeignKey(Query)
    entry = models.ForeignKey(Entry)
    category = models.ForeignKey(Category)
    weight = weight = models.FloatField()
    
    def __cmp__(self,other):
        return cmp(self.weight,other.weight)  
class QueryCategory(models.Model):
    query = models.ForeignKey(Query)
    category = models.ForeignKey(Category)
    count = models.IntegerField()

class Link(models.Model):
    link = models.URLField()
    is_crawled = models.CharField(max_length=1)
    
from wantown.views import query
# from django.dispatch import dispatcher  
signals.request_finished.connect(save_categories)