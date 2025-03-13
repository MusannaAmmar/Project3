from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from apps.administration.models import Category,SubCategory
from django.core.mail import send_mail
from apps.users.utils import send_email
import pyotp
class CustomUserManager(BaseUserManager):
    def create_user(self,email,password,**extra_fields):
        if not email:
            raise ValueError('Enter a valid email')
        email= self.normalize_email(email)
        user= self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save()

        return user
    def create_superuser(self,email,password,**extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_active',True)
        extra_fields.setdefault('is_superuser',True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('User must be is_staff')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('User must be is_superuser')
        return self.create_user(email,password,**extra_fields)
    
class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        USER= 'user'
        PROFESSION= 'profession'
        AGENCY= 'agency'
        ADMIN= 'admin'

    username= models.CharField(max_length=100,null=True,blank=True)
    first_name= models.CharField(max_length=100,null=True,blank=True)
    last_name= models.CharField(max_length=100,null=True,blank=True)
    is_deleted=models.BooleanField(default=False)
    is_active= models.BooleanField(default=False)
    email= models.EmailField(unique=True)
    role = models.CharField(max_length=15, choices=Role.choices, default=Role.USER)
    otp= models.CharField(max_length=6,null=True,blank=True)
    otp_created= models.DateTimeField(auto_now_add=True, null=True,blank=True)
    social_token= models.CharField(max_length=100,null=True,blank=True)
    terms= models.BooleanField(default=False)
    created_at= models.DateTimeField(auto_now_add=True,null=True,blank=True) 


    fcm_token= models.CharField(max_length=100,null=True,blank=True)
    device_id= models.CharField(max_length=100,null=True,blank=True)
    device_name= models.CharField(max_length=100,null=True,blank=True)
    login_device= models.CharField(max_length=100,null=True,blank=True)
    app_version= models.CharField(max_length=100,null=True,blank=True)
    build_number= models.CharField(max_length=100,null=True,blank=True)

    push_notification= models.BooleanField(default=False)
    notification_popup= models.BooleanField(default=False)
    chat_notification= models.BooleanField(default=False)
    community_notification= models.BooleanField(default=False)
    tag_notification= models.BooleanField(default=False)
    new_notification= models.BooleanField(default=False)
    update_notification= models.BooleanField(default=False)
    message_notification= models.BooleanField(default=False)

    new_service= models.BooleanField(default=False)
    new_business=models.BooleanField(default=False)

    qr_code= models.UUIDField(null=True,blank=True)
    qr_code_created_at= models.DateTimeField(null=True,blank=True)

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=[]

    objects= CustomUserManager()


    def __str__(self):
        return self.email
    
    def generate_otp(self):
        totp = pyotp.TOTP('base32secret3232', digits=4)
        otp = totp.now()  # Generate the OTP
        
        # Save OTP and timestamp in the database
        self.otp = otp
        self.otp_created = timezone.now()
        self.save()
        send_email(self.email, otp)

    def verify_otp(self,otp):
        if self.otp and self.otp_created:
            time_elapsed= (timezone.now()- self.otp_created).total_seconds()
            if time_elapsed < 300:
                if otp==self.otp:
                    self.is_verified=True
                    self.save()
                    return True
                return False
            return False
        return False

class UserProfile(models.Model):
    class IdentityChoice(models.TextChoices):
        PASSPORT= 'passport'
        IDCARD= 'id_card'
    user= models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,blank=True,related_name='user_profile')
    first_name= models.CharField(max_length=100)
    last_name= models.CharField(max_length=100)
    address= models.CharField(max_length=200)
    city= models.CharField(max_length=100)
    image= models.ImageField(upload_to='user/image',null=True,blank=True)
    country_code= models.CharField(max_length=100)
    phone_number= models.IntegerField()
    id_type= models.CharField(max_length=100,choices=IdentityChoice.choices, default=IdentityChoice.IDCARD)
    id_number= models.CharField(max_length=14,null=True,blank=True)
    id_image= models.ImageField(upload_to='id/image',null=True,blank=True)
    profile_picture= models.ImageField(upload_to='user/profile', null=True,blank=True)
    description= models.CharField(max_length=1000,null=True,blank=True)


    steps= models.IntegerField(default=0)
    profile_is_completed= models.BooleanField(default=False)

    
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)


    def __str__(self):
        return self.user.email  
    
class ProfessionProfile(models.Model):
    user= models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,blank=True,related_name='profession_profile')
    full_name= models.CharField(max_length=100)
    about= models.TextField()
    email= models.EmailField(unique=True)
    contact= models.CharField(max_length=100,null=True,blank=True)
    website= models.CharField(max_length=100,null=True,blank=True)
    country= models.CharField(max_length=100,null=True,blank=True)
    state= models.CharField(max_length=50,null=True,blank=True)
    image= models.ImageField(upload_to='user/profession')
    city= models.CharField(max_length=50,null=True,blank=True)
    address= models.CharField(max_length=100,null=True,blank=True)
    category= models.ForeignKey(Category,on_delete=models.CASCADE,related_name='profession_category',null=True,blank=True)
    target_customer= models.CharField(max_length=100,null=True,blank=True)
    cash_payment= models.CharField(max_length=100,null=True,blank=True)
    offer_delivery= models.BooleanField(default=False)
    cv= models.FileField(upload_to='profession/cv',null=True,blank=True)
    logo= models.ImageField(upload_to='profession/logo',null=True,blank=True)
    identity_pic=models.ImageField(upload_to='profession/id',null=True,blank=True)
    certificate_pic= models.ImageField(upload_to='prfoession/certificates',null=True,blank=True)
    certificate_type= models.CharField(max_length=100,null=True,blank=True)
    online_payment= models.CharField(max_length=100,null=True,blank=True)
    id_card= models.CharField(max_length=100,null=True,blank=True)
    passport= models.CharField(max_length=100,null=True,blank=True)
    lat= models.BooleanField(default=False)
    lng= models.BooleanField(default=False)
    agency= models.ForeignKey('agency.AgencyProfile',on_delete=models.CASCADE,related_name='agency_profile',null=True,blank=True)
    agency_invite= models.ForeignKey('agency.AgencyProfile',on_delete=models.CASCADE,related_name='agency_invite',null=True,blank=True)
    request_agency= models.ForeignKey('agency.AgencyProfile',on_delete=models.CASCADE,related_name='request_agency',null=True,blank=True)

    steps= models.IntegerField(default=0)
    profile_is_completed= models.BooleanField(default=False)

    jobs_count= models.IntegerField(default=0)
    ratings_count= models.IntegerField(default=0)
    sum_ratings= models.FloatField(null=True,blank=True,default=0)
    ratings= models.FloatField(null=True,blank=True,default=0)

    one_star= models.IntegerField(default=0)
    two_star=models.IntegerField(default=0)
    three_star=models.IntegerField(default=0)
    four_star=models.IntegerField(default=0)
    five_star=models.IntegerField(default=0)


    otp= models.CharField(max_length=6,null=True,blank=True)
    otp_created_at= models.DateTimeField(null=True,blank=True)
    created_at= models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.user.email


class ProfessionSelectedService(models.Model):
    profession= models.ForeignKey(ProfessionProfile,on_delete=models.CASCADE,null=True,blank=True,related_name='selected_service')
    service= models.ForeignKey(SubCategory,on_delete=models.CASCADE,related_name='profession_services',null=True,blank=True)


class Quote(models.Model):
    quotation=models.CharField(max_length=200,null=True,blank=True)
    address= models.CharField(max_length=200,null=True,blank=True)
    budget= models.FloatField(null=True,blank=True)
    message= models.TextField()

    user= models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='quote',null=True,blank=True)
    agency= models.ForeignKey('agency.AgencyProfile',on_delete=models.CASCADE,related_name='agency_quote',null=True,blank=True)
    profession= models.ForeignKey(ProfessionProfile,on_delete=models.CASCADE,related_name='profession_quote',null=True,blank=True)


    def __str__(self):
        return self.quotation



