#coding=utf-8
import re
from django.shortcuts import render,redirect
from models import *
from hashlib import sha1
from django.http import JsonResponse,HttpResponse,HttpResponseRedirect
from . import user_decorator
from df_goods.models import *


# Create your views here.
def register(request):
    context={'title':'用户注册'}
    return render(request,'df_user/register.html',context)

def register_handle(request):
    #接受用户输入
    post=request.POST
    uname=post.get('user_name')
    upwd=post.get('pwd')
    upwd2=post.get('cpwd')
    uemail=post.get('email')
    #判断两次密码
    if upwd!=upwd2:
        return redirect('/user/register/')
    #密码加密
    s1=sha1()
    s1.update(upwd)
    upwd3=s1.hexdigest()

    # 2.参数校验(后端校验)
    # 校验数据的完整性
    if not all([uname, upwd, uemail]):
        return render(request, 'df_user/register.html', {'errmsg': '数据不完整'})

    # 校验邮箱格式
    if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', uemail):
        return render(request, 'df_user/register.html', {'errmsg': '邮箱格式不正确'})

    # 校验用户名是否已注册
    try:
        user = UserInfo.objects.get(uname=uname)
    except UserInfo.DoesNotExist:
        user = None

    if user is not None:
        return render(request, 'df_user/register.html', {'errmsg': '用户名已注册'})

    #创建对象
    user=UserInfo()
    user.uname=uname
    user.upwd=upwd3
    user.uemail=uemail
    user.save()
    #注册成功，转到登陆页面
    return redirect('/user/login/')

def register_exist(request):
    uname=request.GET.get('uname')
    count=UserInfo.objects.filter(uname=uname).count()
    return JsonResponse({'count':count})

def login(request):
    uname=request.COOKIES.get('uname','')
    context={'title':'用户登录','error_name':0,'error_pwd':0,'uname':uname}
    return render(request,'df_user/login.html',context)

def login_handle(request):
    #接受请求信息
    post=request.POST
    uname=post.get('username')
    upwd=post.get('pwd')
    jizhu=post.get('jizhu',0)
    #根据用户名查询对象
    users=UserInfo.objects.filter(uname=uname)#[]
    print uname
    #判断：如果未查到则用户名错，如果查到则判断密码是否正确，正确则转到用户中心
    if len(users)==1:
        s1=sha1()
        s1.update(upwd)
        if s1.hexdigest()==users[0].upwd:
            url=request.COOKIES.get('url','/')
            red = HttpResponseRedirect('/user/info')
            #记住用户名
            if jizhu!=0:
                red.set_cookie('uname',uname)
            else:
                red.set_cookie('uname','',max_age=-1) #max_age=-1立即过期
            request.session['user_id']=users[0].id #判断有没有登录过
            request.session['user_name']=uname
            return red
        else:
            context = {'title': '用户登录', 'error_name': 0, 'error_pwd': 1, 'uname': uname, 'upwd': upwd}
            return render(request,'df_user/login.html',context)
    else:
        context = {'title': '用户登录', 'error_name': 1, 'error_pwd': 0, 'uname': uname, 'upwd': upwd}
        return render(request,'df_user/login.html',context)

def logout(request):
    request.session.flush()
    return redirect('/')


@user_decorator.login
def info(request):
    user_email=UserInfo.objects.get(id=request.session['user_id']).uemail
    #最近浏览
    goods_ids=request.COOKIES.get('goods_ids','')
    goods_ids1=goods_ids.split(',')
    goods_list=[]
    for goods_id in goods_ids1:
        goods_list

    context={'title':'用户中心',
             'user_email':user_email,
             'user_name':request.session['user_name'],
             'page_name':1,
             }
    return render(request,'df_user/user_center_info.html',context)

@user_decorator.login
def order(request):
    context={'title':'用户中心',
             'page_name':1,
    }
    return render(request,'df_user/user_center_order.html',context)

@user_decorator.login
def site(request):
    user = UserInfo.objects.get(id=request.session['user_id'])
    if request.method=='POST':
        post=request.POST
        user.ushou=post.get('ushou')
        user.uaddress=post.get('uaddress')
        user.uyoubian=post.get('uyoubian')
        user.uphone=post.get('uphone')
        user.save()
    context={'title':'用户中心',
             'user':user,
             'page_name':1,
             }
    return render(request,'df_user/user_center_site.html',context)

@user_decorator.login
def calc_tube_length(request):
    user=UserInfo.objects.get(id=request.session['user_id'])
    return render(request,'df_user/user_center_calc_tube_length.html')





