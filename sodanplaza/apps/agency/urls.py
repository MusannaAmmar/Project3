from django.urls import path
from apps.agency.views.profile_views import*
from apps.agency.views.agency_gallery_view import*
from apps.agency.views.dashboard_view import*

profileview_urls= [
    path('agency-profile-view/', AgencyProfileView.as_view(),name='agency_profile'),
    path('agency-update-delete-view/<int:pk>', EditAgencyProfileView.as_view(),name='agency_update'),
    path('agency-slug-view/<str:pk>',AgencyProfileSlugView.as_view(),name='slug_view'),
    path('agency-edit-app/',AgencyProfileEditViewApp.as_view(),name='agency_edit'),
    path('agency-profile-list/',AgencyProfileListView.as_view(),name='agency_profile_list'),
    path('agency-review/',AgencyReviewView.as_view(),name='agency_review'),
    path('agency-gallery/',AgencyGalleryView.as_view(),name='agency_gallery'),
    path('agency-gallery-delete-update/',AgencyGalleryEditDeleteView.as_view(),name='delete_update'),
    path('agency-accept/',AcceptRequestView.as_view(),name='agency_request'),
    path('agency-gallery',GetAgencyGallery.as_view(),name='agency_gallery'),

]

urlpatterns=[
    *profileview_urls
]