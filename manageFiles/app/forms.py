#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django import forms
from django.forms.extras.widgets import SelectDateWidget

department_choices =[('./upload/quality','品质部'),('./upload/technology','技术部')]
reason_choices =(('设计改进','设计改进'),('物料变换','物料变换'))

class Fileform(forms.Form):

    filename = forms.CharField(widget=forms.TextInput(attrs={'class': "uk-width-1-1",'placeholder':"上传附件后自动填写",'readonly':"readonly"}))
    filenumber = forms.CharField(widget=forms.TextInput(attrs={'class': "uk-width-1-1"}))
    department = forms.ChoiceField(widget=forms.Select(attrs={'class': "uk-width-1-1"}),choices=department_choices)
    caption = forms.CharField(widget=forms.TextInput(attrs={'class': "uk-width-1-1"}))
    reason = forms.ChoiceField(widget=forms.Select(attrs={'class': "uk-width-1-1"}),choices=reason_choices)
    department_down = forms.CharField(widget=forms.TextInput(attrs={'class': "uk-width-1-1"}))
    file_path = forms.FileField()
