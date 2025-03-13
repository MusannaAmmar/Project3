from django.urls import path
from apps.users.views.auth_view import*
from apps.users.views.app_profile_views import*

urlpatterns=[
    path('account-register',Register.as_view(),name='registration'),
    path('delete/<int:pk>/',DeleteRegister.as_view(),name='delete'),
    path('login-view/',LoginView.as_view(),name='login'),
    path('otp-verification',VerifyOTPView.as_view(),name='otp_verification'),
    path('forgot-password',ForgotPasswordView.as_view(),name='forgot_password'),
    path('setpassword',SetPassword.as_view(),name='set_password'),
    path('user-profile-edit-view/<int:pk>',UserProfileEditView.as_view(),name='edit_view'),
    path('profession-profile/<int:pk>',ProfessionProfileView.as_view(),name='profession_profile'),
    path('profession-profile-edit/<int:pk>',ProfessionProfileEditView.as_view(),name='profession_edit'),
    path('user-view',GetUserView.as_view(),name='get_view'),
]
