from rest_framework.urls import path
from apps.profession.views.homepage_view import*
from apps.profession.views.gig_view import*

urlpatterns= [
    path('profession-list/',GetProfessionalsView.as_view(),name='profession_list'),
    path('profession-category/',ProfessionbyCategory.as_view(),name='profession_category'),
    path('gig-view/',GigView.as_view(),name='gig_view'),
    path('gig-slug-view',GetGigbySlugView.as_view(),name='slug_view'),
]