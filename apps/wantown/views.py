# -*- coding: utf-8 -*-
import datetime, re
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.datastructures import MultiValueDictKeyError
from apps.wantown import dao
from apps.wantown.forms import UserCreationForm

email_re = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"' # quoted-string
    r')@(?:[A-Z0-9-]+\.)+[A-Z]{2,6}$', re.IGNORECASE)  # domain

def index(request):
    return render_to_response('index.html', {'objects':dao.list()}, context_instance=RequestContext(request))

@login_required
def clone(request, id):
    try:
        object = dao.get(id)
    except :
        raise Http404
    key = dao.save_clone(object, request.user)
    request.user.message_set.create(message='\"' + object.what + '\" 已经添加到您的名下!'.decode('utf-8'))
    return HttpResponseRedirect('/wantown/view/id/' + id)
    

def login(request):
    return render_to_response('login.html', context_instance=RequestContext(request))

def login_by(request, by):
    if by:
        data = request.POST.copy()
        #form = LoginForm(data)
        if data:
            user = auth.authenticate(username=data.get('username', ''), password=data.get('password', ''))
            if user and user.is_active:
                # Correct password, and the user is marked "active"
                auth.login(request, user)
                request.session['user'] = user 
                return HttpResponseRedirect("/")
            else:
                return render_to_response('login.html', {'error_email':'用户名或密码有误.'}, context_instance=RequestContext(request))

    
    return render_to_response('login.html', context_instance=RequestContext(request))

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')

def register(request):
    form = UserCreationForm()
    data, errors = {}, {}
    return render_to_response('register.html', {'register_form' : form}, context_instance=RequestContext(request))

def register_submit(request):    
    if request.method == 'POST':
        data = request.POST.copy()    
        form = UserCreationForm(data)
        if form.is_valid():
            new_user = form.save(data)
            return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")
    return render_to_response("register.html", {'register_form' : form, 'data' : data}, context_instance=RequestContext(request))


def search(request, which, what):
        return render_to_response('index.html', {'objects':dao.query(which, what)}, context_instance=RequestContext(request))
def post(request, step):
    if request.method == 'POST':
        who = request.user
        what = request.POST['what']
        which = request.POST['which']
        data = ''
        if step == '1':
            data = {'what':what, 'which':which}
            return render_to_response('post.html', {'object':data}, context_instance=RequestContext(request))
        elif step == '2':
            available = request.POST.get('available', 'no')
            category = request.POST.get('category', '无').decode('utf-8')
            if not category:
                category = '无'.decode('utf-8')
            if not who:
                email = request.POST.get('email', 'unknown@unknown.com').decode('utf-8')
                if not email:
                    email = 'unknown@unknown.com'                
                who = AnonymousUser(email)
            data = dao.save(who, what, which, dao.save_category(category), available)
            return HttpResponseRedirect('/wantown/view/id/' + data.__str__())
    #用户直接输入这个url,则返回到首页
    return HttpResponseRedirect('/')
    
def list(request):
    return render_to_response('index.html', {'objects':dao.list()}, context_instance=RequestContext(request))

def view(request, id):
    try:
        object = dao.get(id)
    except :
        raise Http404
    return render_to_response('view.html', {'object':object}, context_instance=RequestContext(request))

