from django.urls import path
from apps.administration.views.category_view import*
from apps.administration.views.dashboard_view import*

urlpatterns=[
    path('search-subcategory',ListSubcategoryView.as_view(),name='search_bar'),
    path('user-dashboard',AdminDashboardUserView.as_view(),name='user_dashboard'),
    path('useradmin-dashboard',AdminDashboardProfessionView.as_view(),name='user_dashboard'),
]