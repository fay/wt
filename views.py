# -*- coding: utf-8 -*-
import datetime, re,logging
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.datastructures import MultiValueDictKeyError
from dot import dao
from apps import wantown
from django.contrib.sessions.models import Session
from django.core.paginator import Paginator, InvalidPage, EmptyPage
logger = logging.getLogger('spy')
hdlr = logging.FileHandler('logs/query.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


class ResultWrapper(object):
    def __init__(self, entry, score):
        self.entry = entry
        self.score = score
def index(request):
    feeds_num = wantown.dao.get_total_feeds()
    entries_num = wantown.dao.get_total_entries()
    return render_to_response('x/index.html', {'feeds_num':feeds_num, 'entries_num':entries_num}, context_instance=RequestContext(request))

def query(request,category_what=None,query=None):
    if not (category_what and query):
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
        (entries, scores, total,phrases,label_doc) = dao.query(defer, page,category_what)
        i = 0
        for result in entries:
            results.append(ResultWrapper(result, scores[i]))
            i = i + 1
        
        categories = wantown.dao.search_category(query)
        #for c in categories:
            #c = c.what.lower()
            #if c != query:
                #cats[c] = None
                
        paginator = ''
        pages_num = total / dao.PAGE_SIZE + (total % dao.PAGE_SIZE and 1) or 0
        if page >= pages_num:
            page = pages_num
        if category_what:
            prelink = '<a href=\"/x/query/category/' + category_what + "/" + query + "/?page="
        else:
            prelink = '<a href=\"/x/query/?query=' + query + '&page='
        if page != 0:
            if page != 1:
                paginator = prelink + str(page - 1) + '\">Pre</a> | '
            for i in range((10 > pages_num and pages_num) or 10):
                paginator = paginator + ' ' + prelink + \
                                    str(i + (page / 10 + (page % 10 and 1) or 0)) + '\">  ' + str(i + (page / 10 + (page % 10 and 1) or 0)) + ' </a> | '
            if page != pages_num:
                paginator = paginator + prelink + str(page + 1) + '\">Next</a>'
    return render_to_response('x/results.html', {'results':results, 'query':query, 'cats':categories[:10], 'defer':defer, 'total':total, 'page':page, 'paginator':paginator,'phrases':phrases,'label_doc':label_doc} , context_instance=RequestContext(request))


def redirect(request, entry_id, keyword, url):
    qec = wantown.dao.get_qec_by_qe(keyword, entry_id)
    for i in qec:
        wantown.dao.save_keyword(keyword, i.category.id)
    logger.info(str(request.session.session_key) + " " + keyword + " " + entry_id + " " + url)
    return HttpResponseRedirect(url)

def view(request,id):
    id = int(id)
    entry = wantown.models.Entry.objects.get(id=id)
    return render_to_response('x/view.html', {'entry':entry},context_instance=RequestContext(request))
