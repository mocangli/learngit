#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time,uuid,json
from django.db import models
from django.http import JsonResponse


# Create your models here.
def get_file_path(instance,filename):
    productionName = instance.department
    return '%s/%s'% (productionName,filename)

def next_id():
    # 当前时间再集合uuid4就不会产生重复ID的问题了
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)

class User(models.Model):

    id = models.CharField(primary_key=True, default=next_id, max_length=50)
    email = models.EmailField('邮箱',max_length=50)
    passwd = models.CharField(max_length=50)
    admin = models.BooleanField('管理员')
    name = models.CharField('用户名',max_length=50)
    image = models.CharField(max_length=500)
    created_at = models.DateField('创建时间',auto_now_add=True)

    def toJSON(self):
        fields = []
        for field in self._meta.fields:
            fields.append(field.name)
        d = {}
        for attr in fields:
            d[attr] = getattr(self, attr)
        return JsonResponse(d)

    def __str__(self):
        return self.name
        

class Myfile(models.Model):
    """docstring for Myfile"""
    id = models.CharField(primary_key=True, default=next_id, max_length=50)
    filename        = models.CharField('文件名',max_length=50,unique=True)
    filenumber      = models.CharField('图号',max_length=50)
    department      = models.CharField('部门',max_length=50)
    caption         = models.CharField('说明',max_length=50)
    reason          = models.CharField('变更原因',max_length=50)
    department_down = models.CharField('下发部门',max_length=50)
    created_at      = models.DateTimeField('修改时间',auto_now=True) 
    user_name       = models.CharField('创建者',max_length=50)
    user_id         = models.CharField(max_length=50)
    file_path       = models.FileField('路径',upload_to = get_file_path)
    file_display    = models.BooleanField('是否可见',default=False)
    dispose_user    = models.CharField('处理者',max_length=50,null=True)

    def toDict(self):
        fields = []
        for field in self._meta.fields:
            fields.append(field.name)
        d = {}
        for attr in fields:
            d[attr] = getattr(self, attr)
        return d
        
    def __str__(self):
        return self.filename
# 流程
class Review(models.Model):
    """docstrinReviewssName"""
    id = models.CharField(primary_key=True, default=next_id, max_length=50)
    file_id = models.CharField(max_length=50, null=True)
    user_name  = models.CharField('创建者',max_length=50,null=True)
    proofread_user  = models.CharField('校对者',max_length=50)
    review_user     = models.CharField('审核者',max_length=50)
    countersign_user= models.CharField('会签者',max_length=50)
    approved_user   = models.CharField('批准者',max_length=50)
    Issued_user     = models.CharField('下发者',max_length=50)
    dispose_user    = models.CharField('处理者',max_length=50)

    def toDict(self):
        fields = []
        for field in self._meta.fields:
            fields.append(field.name)
        d = {}
        for attr in fields:
            d[attr] = getattr(self, attr)
        return d
# 签审意见
class Comment(models.Model):

    id = models.CharField(primary_key=True, default=next_id, max_length=50)
    review_id   = models.CharField(max_length=50)
    user_id     = models.CharField(max_length=50)
    user_name   = models.CharField(max_length=50)
    content     = models.TextField()
    created_at  = models.DateField('创建时间',auto_now_add=True)

    def toDict(self):
        fields = []
        for field in self._meta.fields:
            fields.append(field.name)
        d = {}
        for attr in fields:
            d[attr] = getattr(self, attr)
        return d
                		