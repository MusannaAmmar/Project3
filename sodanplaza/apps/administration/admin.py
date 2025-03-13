from django.contrib import admin

# Register your models here.

from apps.administration.models import *


admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(VideoTutorial)
admin.site.register(Language)
admin.site.register(SiteSettings)