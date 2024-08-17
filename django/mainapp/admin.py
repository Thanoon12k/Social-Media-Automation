from django.contrib import admin

from .models import CustomUser
from .models import SocialAccount





class usersAdmin(admin.ModelAdmin):
    list_display = ['username','hoppy']
    
    

admin.site.register(SocialAccount)
admin.site.register(CustomUser,usersAdmin)