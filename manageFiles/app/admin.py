from django.contrib import admin
from .models import User,Myfile,Review

# Register your models here.

class UserAdmin(admin.ModelAdmin):
	"""docstring for User"""
	list_display = ('name','email','created_at','admin',)
		
class MyfileAdmin(admin.ModelAdmin):
	"""docstring for MMyfileAdmin"""
	list_display = ('filename','filenumber','created_at','user_name','file_path',)

class ReviewAdmin(admin.ModelAdmin):
	"""docstring for MMyfileAdmin"""
	list_display = ('proofread_user','user_name','review_user','countersign_user','approved_user','Issued_user','dispose_user')
		
admin.site.register(User,UserAdmin)
admin.site.register(Myfile,MyfileAdmin)
admin.site.register(Review,ReviewAdmin)