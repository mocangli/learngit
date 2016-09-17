#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re,logging,hashlib,base64,time,json,os

from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse,FileResponse,Http404,StreamingHttpResponse
from django.core.serializers import serialize,deserialize
from app.forms import Fileform
from app.models import User,Myfile,Review,Comment,next_id
from app.apis import Page, APIValueError, APIResourceNotFoundError, APIError

# Create your views here.

# email的匹配正则表达式
_RE_EMAIL = re.compile(
    r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
# 密码的匹配正则表达式
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')

COOKIE_NAME = 'awesession'
_COOKIE_KEY = 'Awesome'

# 获取页数，主要是做一些容错处理

def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p

# 构建coolie
def user2cookie(user, max_age):
    # build cookie string by: id-expires-sha1
    # 过期时间是当前时间+设置的有效时间
    expires = str(int(time.time() + max_age))
    # 构建cookie存储的信息字符串
    s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
    L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    # 用-隔开，返回
    return '-'.join(L)

# 解析coolie
def cookie2user(cookie_str):
    # cookie_str是空则返回
    if not cookie_str:
        return None
    try:
        # 通过'-'分割字符串
        L = cookie_str.split('-')
        # 如果不是3个元素的话，与我们当初构造sha1字符串时不符，返回None
        if len(L) != 3:
            return None
        # 分别获取到用户id，过期时间和sha1字符串
        uid, expires, sha1 = L
        # 如果超时，返回None
        if int(expires) < time.time():
            return None
        # 根据用户id查找库，对比有没有该用户
        user = User.objects.get(pk=uid)
        # 没有该用户返回None
        if user is None:
            return None
        # 根据查到的user的数据构造一个校验sha1字符串
        s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY)
        # 比较cookie里的sha1和校验sha1，一样的话，说明当前请求的用户是合法的
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user.passwd = '******'
        # 返回合法的user
        return user
    except Exception as e:
        logging.exception(e)
        return None

def get_auth(request):
    user = None
    # 获取到cookie字符串
    cookie_str = request.COOKIES.get(COOKIE_NAME,'')
    if cookie_str:
        # 通过反向解析字符串和与数据库对比获取出user
        user = cookie2user(cookie_str) 
    # 执行下一步
    return user

def page2dict(std):
    return {
    'item_count'     : std.item_count,
    'page_count'     : std.page_count,
    'page_index'     : std.page_index,
    'page_size'     : std.page_size,
    'offset'         : std.offset,
    'limit'         : std.limit,
    'has_previous'	:	std.has_previous,
    'has_next'		:	std.has_next
    }

# GET、POST 请求分流
def method_splitter(request, GET=None, POST=None):
    if request.method == 'GET' and GET is not None:
        return GET(request)
    elif request.method == 'POST' and POST is not None:
        return POST(request)
    raise Http404

# 构建返回信息
def creat_response(user):

    # 返回的是json数据，所以设置content-type为json的
    r = HttpResponse(content_type='application/json')
    # 添加cookie
    r.set_cookie(COOKIE_NAME, user2cookie(
        user, 86400), max_age=86400, httponly=True)
    # 只把要返回的实例的密码改成'******'，库里的密码依然是正确的，以保证真实的密码不会因返回而暴漏
    user.passwd = '******'
    # 把对象转换成json格式返回
    r.content = user.toJSON()
    print(r.content)
    return r
# 首页
def index(request):
    page = request.GET.get('page','1')
    user = get_auth(request)
    # 用户非管理员或不存在,将会重定向到登录页面
    if user is None: #or not user.admin:
        return HttpResponseRedirect('/signin/')
    return render(request,'index.html',{'user':user,'page_index':get_page_index(page)})

# 获取工作流信息
def api_files(request):
    # 获取文件信息
    user = get_auth(request)
    page = request.GET.get('page','1')
    page_index = get_page_index(page)
    print(user.pk)
    num = Myfile.objects.filter(user_id=user.pk).filter(file_display=False).count()
    print(num)
    p = Page(num, page_index)
    if num == 0:
        return JsonResponse(dict(page=page2dict(p), files=()))
    files = Myfile.objects.filter(user_id=user.pk).filter(file_display=False).order_by('-created_at')[p.offset: p.offset+p.limit]
    return JsonResponse({'page':page2dict(p), 'files':json.loads(serialize('json',files))})
# 注册
def register(request):
    user = get_auth(request)
    return render(request,'register.html',{'user':user})

# 注册请求

def api_register_user(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        name = data['name']
        email = data['email']
        passwd = data['passwd']
        # 判断name是否存在，且是否只是'\n', '\r',  '\t',  ' '，这种特殊字符
        if not name or not name.strip():
            raise APIValueError('name')
        # 判断email是否存在，且是否符合规定的正则表达式
        if not email or not _RE_EMAIL.match(email):
            raise APIValueError('email')
        # 判断passwd是否存在，且是否符合规定的正则表达式
        if not passwd or not _RE_SHA1.match(passwd):
            raise APIValueError('passwd')

        # 查一下库里是否有相同的email地址，如果有的话提示用户email已经被注册过
        users =  User.objects.filter(email=email).count()
        if users > 0:
            raise APIError('register:failed', 'email', 'Email is already in use.')

        # 生成一个当前要注册用户的唯一uid
        uid = next_id()
        # 构建shal_passwd
        sha1_passwd = '%s:%s' % (uid, passwd)

        admin = False
        if email == 'admin@163.com':
            admin = True

        # 创建一个用户（密码是通过sha1加密保存）
        user = User(id=uid, name=name.strip(), email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(),
                    image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest(), admin=admin)

        # 保存这个用户到数据库用户表
        user.save()
        print('save user OK')
        return creat_response(user)
# 登录    
def signin(request):
    return render(request,'signin.html')

# 登陆请求    
def api_authenticate(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        email = data['email']
        passwd = data['passwd']
        # 如果email或passwd为空，都说明有错误
        if not email:
            raise APIValueError('email', 'Invalid email')
        if not passwd:
            raise APIValueError('passwd', 'Invalid  passwd')
        # 根据email在库里查找匹配的用户
        users =  User.objects.filter(email=email)
        # 没找到用户，返回用户不存在
        if users.count() == 0:
            raise APIValueError('email', 'email not exist')
        # 取第一个查到用户，理论上就一个
        user = users[0]
        # 按存储密码的方式获取出请求传入的密码字段的sha1值
        sha1 = hashlib.sha1()
        sha1.update(user.id.encode('utf-8'))
        sha1.update(b':')
        sha1.update(passwd.encode('utf-8'))
        # 和库里的密码字段的值作比较，一样的话认证成功，不一样的话，认证失败
        if user.passwd != sha1.hexdigest():
            raise APIValueError('passwd', 'Invalid passwd')
        return creat_response(user)

# 注销
def signout(request):
    referer = request.META['HTTP_REFERER']
    print('referer:%s'%referer)
    r = HttpResponseRedirect(referer or '/')
    # 清理掉cookie的用户信息数据
    r.delete_cookie(COOKIE_NAME)
    print('user signed out')
    return r
# -------------------------------> 文件管理 <------------------------------------

# 上传文件
def fileupload(request):
    user = get_auth(request)
    # 用户非管理员或不存在,将会重定向到登录页面
    if user is None or not user.admin:
        return HttpResponseRedirect('/signin/')
    if request.method == "POST":
        form = Fileform(request.POST,request.FILES)
        if form.is_valid():
            #获取表单信息
            filename = form.cleaned_data['filename']
            filenumber = form.cleaned_data['filenumber']
            department = form.cleaned_data['department']
            caption = form.cleaned_data['caption']
            reason = form.cleaned_data['reason']
            department_down = form.cleaned_data['department_down']
            file_path = form.cleaned_data['file_path']

            #写入数据库
            myfile = Myfile()
            myfile.filename = filename
            myfile.filenumber = filenumber
            myfile.department = department
            myfile.caption = caption
            myfile.reason = reason
            myfile.department_down = department_down
            myfile.file_path = file_path
            myfile.user_name = user.name
            myfile.user_id = user.id
            myfile.save()

            return HttpResponseRedirect('/')
    else:
        form = Fileform()
    return render(request,'upload.html',{'form':form,'user':user})

# 读取文件的迭代器    
def file_iterator(file_path, chunk_size=512):
    with open(file_path,'rb') as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break
# 下载文件
def file_download(request):
    id = request.GET.get('id')
    print(id)
    file = Myfile.objects.get(pk=id)
    print(file)
    the_file_path = file.file_path.path
    the_file_name = file.filename.encode('utf-8').decode("ISO-8859-1")
    response = FileResponse(file_iterator(the_file_path))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename=%s'%the_file_name
    return response

# 删除文件
def file_delete(request):
    id = request.GET.get('id')
    print(id)
    file = Myfile.objects.get(pk=id)
    if file is None:
        raise APIResourceNotFoundError('file')
    file.file_path.delete(save=True)
    file.delete()
    return JsonResponse(dict(id=id))

# 文件搜索：
def search_file(request):
    user = get_auth(request)
    page = request.GET.get('page','1')
    filenum = request.GET.get('filenum',None)
    return render(request,'search.html',{'user':user,"filenum":json.dumps(filenum),'page_index':get_page_index(page)})


def api_file_search(request):
    user = get_auth(request)
    page = request.GET.get('page','1')
    page_index = get_page_index(page)
    filenum = request.GET.get('filenum',None) or request.session.get('filenum',default=None)
    request.session['filenum'] = filenum
    if filenum!=None and filenum.startswith('*'):
        filenum = filenum.strip('*')
        files = Myfile.objects.filter(filename__icontains=filenum).exclude(file_display=False)
    else:
        files = Myfile.objects.filter(filenumber=filenum).exclude(file_display=False)
    num = len(files)
    p = Page(num, page_index)
    files = files.order_by('-created_at')[p.offset: p.offset+p.limit]
    return JsonResponse({'page':page2dict(p), 'files':json.loads(serialize('json',files))})
    #return render(request,'search.html',{'user':user,'page':page2dict(p),'files':json.loads(serialize('json',files))})

# ------------------------------>审批流程 <----------------------------------

# 创建审批团队
def checkForm(request):
    id = request.GET.get('id')
    print(id)
    user = get_auth(request)

    return render(request,'checkForm.html',{'user':user,'id':id})

# 进入审批流程
def api_checkForm(request):
    user = get_auth(request)
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))

        review = Review()
        review.proofread_user = data['proofread']
        review.review_user = data['review']
        review.countersign_user = data['countersign']
        review.approved_user = data['approved']
        review.Issued_user = data['Issued']
        review.dispose_user = data['proofread']
        review.file_id = data['file_id']
        review.user_name = user.name
        review.save()
        file=Myfile.objects.get(pk=review.file_id)
        file.dispose_user = review.dispose_user
        file.save()
        return JsonResponse({'review':review.toDict()})

# 流程签审表单
def process_form(request):
    id = request.GET.get('id')
    user = get_auth(request)
    return render(request,'process_form.html',{'user':user,'id':id})

# 获取流程数据
def api_process(request):
    file_id = request.GET.get('id')
    user = get_auth(request)
    review = Review.objects.get(file_id=file_id)
    id = review.id
    print('id:%s'%id)
    comments = Comment.objects.filter(review_id=id)
    files = Myfile.objects.filter(pk=file_id)
    return JsonResponse({'review':review.toDict(), 'comments':json.loads(serialize('json',comments)),'files':json.loads(serialize('json',files))})
# 进入下一节点
def api_create_comment(request):
    data = json.loads(request.body.decode('utf-8'))
    file_id = data['id']
    content = data['content']
    # 对流程节点填写审批意见
    user = get_auth(request)
    # 必须为登陆状态下，评论
    if user is None:
        raise APIPermissionError('user')
    # 意见不能为空
    if not content or not content.strip():
        raise APIValueError('content')
    # 查询一下流程id是否有对应的流程
    review = Review.objects.get(file_id=file_id)
    # 没有的话抛出错误
    if review is None:
        raise APIResourceNotFoundError('review')
    # 完成流程的传递
    l = [review.user_name,
        review.proofread_user,
        review.review_user,
        review.countersign_user,
        review.approved_user,
        review.Issued_user,
        'success']
    i = 0
    for i in range(len(l)):
        if l[i] == user.name:
            print(l[i])
            review.dispose_user = l[i+1]
            review.save()
    file = Myfile.objects.get(pk=file_id)
    file.dispose_user = review.dispose_user
    if review.dispose_user == 'success':
        print('设置dispose_user')
        file.file_display = True
    file.save()
    # 构建一条评论数据
    comment = Comment(review_id=review.id, user_id=user.id, user_name=user.name, content=content.strip())
    # 保存到评论表里
    comment.save()
    print(file.toDict())
    return JsonResponse({'comment':comment.toDict()})

# 退回申请人
def api_backprocess(request):
    data = json.loads(request.body.decode('utf-8'))
    file_id = data['id']
    content = data['content']
    print(file_id)
    # 对某个博客发表评论
    user = get_auth(request)
    # 必须为登陆状态下，评论
    if user is None:
        raise APIPermissionError('user')
    # 评论不能为空
    if not content or not content.strip():
        raise APIValueError('content')
    # 查询一下博客id是否有对应的博客
    file = Myfile.objects.get(pk=file_id)
    review = Review.objects.get(file_id=file_id)
    review.dispose_user = file.user_name
    review.save()
    file.dispose_user = review.dispose_user
    file.save()
    # 构建一条评论数据
    comment = Comment(review_id=review.id, user_id=user.id, user_name=user.name, content=content.strip())
    # 保存到评论表里
    comment.save()
    return JsonResponse({'comment':comment.toDict()})

# 待签审文件列表
def sign_off_files(request):
    page = request.GET.get('page','1')
    page_index = get_page_index(page)
    user = get_auth(request)
    if user==None:
        return HttpResponseRedirect('/')
    files = Myfile.objects.filter(dispose_user=user.name).filter(file_display=False)
    num = len(files)
    print(num)
    p = Page(num, page_index)
    files = files.order_by('-created_at')[p.offset: p.offset+p.limit]
    return render(request,'signOff_files.html',{'user':user,'page':page2dict(p),'files':json.loads(serialize('json',files))})







