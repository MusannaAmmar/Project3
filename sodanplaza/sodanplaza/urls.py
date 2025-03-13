from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
# )


from django.contrib import admin
from django.urls import path

admin_urls = [
    path('admin/', admin.site.urls),
]


swagger_urls = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

apps_urls = [
    path('api/', include('apps.users.urls')),
    path('api/', include('apps.agency.urls')),
    path('api/', include('apps.administration.urls')),
    path('api/', include('apps.profession.urls')),
    # path('api/', include('apps.chat.urls')),
]

urlpatterns=[
    *admin_urls,*swagger_urls,*apps_urls
]