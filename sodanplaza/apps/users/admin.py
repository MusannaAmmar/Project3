from django.contrib import admin

# Register your models here.
from apps.users.models import *


admin.site.register(CustomUser)
admin.site.register(UserProfile)
admin.site.register(ProfessionProfile)
admin.site.register(ProfessionSelectedService)
admin.site.register(Quote)
