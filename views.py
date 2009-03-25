# -*- coding: utf-8 -*-
import datetime, re
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.datastructures import MultiValueDictKeyError
from dot import dao
from apps import wantown
from django.core.paginator import Paginator, InvalidPage, EmptyPage


class ResultWrapper(object):
    def __init__(self, entry, score):
        self.entry = entry
        self.score = score
def index(request):
    feeds_num = wantown.dao.get_total_feeds()
    entries_num = wantown.dao.get_total_entries()
    return render_to_response('x/index.html', {'feeds_num':feeds_num, 'entries_num':entries_num}, context_instance=RequestContext(request))

def query(request):
    query = request.GET.get('query', '')
    if not query:
        return index(request)
    defer = request.GET.get('defer', query)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    results = []
    if query:
        (entries, scores, keywords, total,phrases) = dao.query(defer, page)
        i = 0
        for result in entries:
            results.append(ResultWrapper(result, scores[i]))
            i = i + 1
        
        categories = wantown.dao.search_category(query)
        cats = {}
        for c in categories:
            c = c.what.lower()
            if c != query:
                cats[c] = None
        paginator = ''
        pages_num = total / dao.PAGE_SIZE + (total % dao.PAGE_SIZE and 1) or 0
        if page >= pages_num:
            page = pages_num
        if page != 0:
            if page != 1:
                paginator = '<a href=\"/x/query/?query=' + query + '&page=' + str(page - 1) + '\">Pre</a> | '
            for i in range((10 > pages_num and pages_num) or 10):
                paginator = paginator + ' <a href=\"/x/query/?query=' + query + '&page=' + \
                                    str(i + (page / 10 + (page % 10 and 1) or 0)) + '\">  ' + str(i + (page / 10 + (page % 10 and 1) or 0)) + ' </a> | '
            if page != pages_num:
                paginator = paginator + '<a href=\"/x/query/?query=' + query + '&page=' + str(page + 1) + '\">Next</a>'
    return render_to_response('x/results.html', {'results':results, 'keywords':keywords, 'query':query, 'cats':cats.keys(), 'defer':defer, 'total':total, 'page':page, 'paginator':paginator,'phrases':phrases} , context_instance=RequestContext(request))

def redirect(request, category_id, keyword, url):
    wantown.dao.save_keyword(keyword, int(category_id))
    return HttpResponseRedirect(url)
