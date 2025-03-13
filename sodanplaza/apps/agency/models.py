from django.db import models
from apps.users.models import CustomUser,ProfessionProfile
from apps.administration.models import *

class AgencyProfile(models.Model):
    bussiness_logo= models.ImageField(upload_to='business/logo',null=True,blank=True)
    business_name= models.CharField(max_length=100,null=True,blank=True)
    about_business= models.TextField()
    business_email= models.EmailField(unique=True)
    business_website=models.CharField(max_length=100,null=True,blank=True)
    business_contact= models.CharField(max_length=100,null=True,blank=True)
    country= models.CharField(max_length=100,null=True,blank=True)
    state= models.CharField(max_length=100,null=True,blank=True)
    city= models.CharField(max_length=100,null=True,blank=True)
    category= models.CharField(max_length=200,null=True,blank=True)
    target_customer= models.CharField(max_length=100,null=True,blank=True)
    cash_payment= models.BooleanField(default=False)
    online_payment= models.BooleanField(default=False)
    offer_delivery= models.BooleanField(default=False)
    certificate_type= models.CharField(max_length=100,null=True,blank=True)
    certificate_image= models.ImageField(upload_to='certificate/image/')
    description= models.TextField()
    business_lat= models.FloatField(null=True,blank=True)
    business_lng= models.FloatField(null=True,blank=True)
    meta_title= models.CharField(max_length=100,null=True,blank=True)
    employee_count= models.IntegerField(default=0)
    jobs_count= models.IntegerField(default=0)


    rating_count= models.IntegerField(null=True,blank=True,default=0)
    sum_rating= models.FloatField(null=True,blank=True,default=0)
    ratings= models.FloatField(null=True,blank=True,default=0)

    one_star=models.IntegerField(default=0)
    two_star=models.IntegerField(default=0)
    three_star=models.IntegerField(default=0)
    four_star=models.IntegerField(default=0)
    five_star=models.IntegerField(default=0)

    user= models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='user_field')
    steps= models.IntegerField(default=0)
    profile_completed= models.BooleanField(default=False)

    is_active= models.BooleanField(default=False)
    created_at= models.DateTimeField(auto_now_add=True,null=True,blank=True)
    category= models.ForeignKey(Category,on_delete=models.CASCADE,related_name='agency_category',null=True,blank=True)


    def __str__(self):
        return self.business_name
    
class OwnerProfile(models.Model):
    agency= models.ForeignKey(AgencyProfile,on_delete=models.CASCADE,related_name='owner_profile')
    owner_name= models.CharField(max_length=100,null=True,blank=True)
    owner_email=models.EmailField(unique=True)
    owner_contact= models.CharField(max_length=100,null=True,blank=True)

    def __str__(self):
        return self.owner_name
    
class AgencyGallery(models.Model):
    agency= models.ForeignKey(AgencyProfile,on_delete=models.CASCADE,related_name='agency_gallery')
    image= models.ImageField(upload_to='gallery/agency')

class AgencyServices(models.Model):
    agency= models.ForeignKey(AgencyProfile,on_delete=models.CASCADE,related_name='agency_service',null=True,blank=True)
    service= models.ForeignKey(SubCategory,on_delete=models.CASCADE,related_name='services',null=True,blank=True)

class AgencyReview(models.Model):
    agency= models.ForeignKey(AgencyProfile,on_delete=models.CASCADE,related_name='agency_review')
    rating= models.IntegerField(default=0,null=True,blank=True)
    comments= models.TextField()

    user= models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='agency_user')
    profession= models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='agency_profession')
    created_at= models.DateTimeField(auto_now_add=True,null=True,blank=True)

class AgencyEmploye(models.Model):
    agency= models.ForeignKey(AgencyProfile,on_delete=models.CASCADE,related_name='agency_employe')
    profession= models.ForeignKey(ProfessionProfile,on_delete=models.CASCADE,related_name='profession')

class InviteMembers(models.Model):
    profession= models.ForeignKey(ProfessionProfile,on_delete=models.CASCADE,related_name='invite_members')
    agency=models.ForeignKey(AgencyProfile,on_delete=models.CASCADE,related_name='invite_agency')
    invite_status= models.BooleanField(default=False)

    def __str__(self):
        return self.invite_status






class AgencyHours(models.Model):
    agency = models.ForeignKey(AgencyProfile, on_delete=models.CASCADE, related_name="hours")
    day_of_week = models.CharField(max_length=10)  # e.g., "Monday"
    opening_time = models.TimeField()
    closing_time = models.TimeField()

    class Meta:
        unique_together = ("agency", "day_of_week")

    def __str__(self):
        return f"{self.agency.business_name} - {self.day_of_week}: {self.opening_time} - {self.closing_time}"
