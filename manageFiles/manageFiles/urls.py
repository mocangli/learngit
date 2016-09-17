#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""manageFiles URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from app import views
urlpatterns = [
	url(r'^register/$',views.register),								# 注册
	url(r'^$',views.index),											# 首页
	url(r'^api/files',views.api_files),								# 文件管理
	url(r'^api/users',views.api_register_user),					    # 注册请求
	url(r'^signin/$',views.signin),									# 登陆
    url(r'^signout/$',views.signout),                               # 注销
	url(r'^api/authenticate',views.api_authenticate),				# 登陆请求
	url(r'^api/fileupload/$',views.fileupload),					    # 文件上传
    url(r'^api/filedownload/$',views.file_download),                # 文件下载
    url(r'^api/searchfile',views.api_file_search),                  # 文件搜索
    url(r'^searchfile/',views.search_file),                         # 文件搜索
    url(r'^api/filedelete/$',views.file_delete),                    # 文件删除
    url(r'^checkForm/$',views.checkForm),                           # 审批团队表单
    url(r'^api/checkForm/$',views.api_checkForm),                   # 保存团队
    url(r'^signOff/$',views.sign_off_files),                        # 待签审文件列表
    url(r'^processForm/$',views.process_form),                      # 审批表单
    url(r'^api/process/$',views.api_process),                       # 获取流程节点
    url(r'^api/processForm/comments/$',views.api_create_comment),   # 审批意见/进入下一节点
    url(r'^api/backprocess/$',views.api_backprocess),               # 退回申请人


    url(r'^admin/', admin.site.urls),
]
