from django.db import models
from apps.administration.models import Category,SubCategory
from apps.agency.models import AgencyProfile

class Gig(models.Model):
    title= models.CharField(max_length=100,null=True,blank=True)
    description= models.TextField()
    created_at= models.DateTimeField(auto_now_add=True,null=True,blank=True)

    is_available= models.BooleanField(default=False)
    is_publish= models.BooleanField(default=False)
    is_archived= models.BooleanField(default=False)
    meta_title= models.CharField(max_length=100,null=True,blank=True)
    slug= models.CharField(max_length=100,null=True,blank=True)
    category= models.ForeignKey(Category,on_delete=models.CASCADE,related_name='gig_category',null=True,blank=True)
    profession= models.ForeignKey('users.ProfessionProfile',on_delete=models.CASCADE,related_name='users_profession',null=True,blank=True)
    category= models.ForeignKey(Category,on_delete=models.CASCADE,related_name='gig_category',null=True,blank=True)


    def __str__(self):
        return self.title

class GigSelectedService(models.Model):
    gig= models.ForeignKey(Gig,on_delete=models.CASCADE,related_name='gig_service',null=True,blank=True)
    service= models.ForeignKey(SubCategory,on_delete=models.CASCADE,related_name='service_gig',null=True,blank=True)

    def __str__(self):
        return self.service.title

class GigReview(models.Model):
    gig= models.ForeignKey(Gig,on_delete=models.CASCADE,related_name='gig_review',null=True,blank=True)
    comment= models.TextField()
    rating= models.FloatField()

    user= models.ForeignKey('users.CustomUser',on_delete=models.CASCADE,related_name='review_user',null=True,blank=True)
    profession= models.ForeignKey('users.ProfessionProfile',on_delete=models.CASCADE,related_name='profession_review',null=True,blank=True)

    created_at= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.gig

class GigFaq(models.Model):
    gig= models.ForeignKey(Gig,on_delete=models.CASCADE,related_name='gig_faq',null=True,blank=True)
    question= models.TextField()
    answer= models.TextField()

    def __str__(self):
        return self.gig


class RequestAttachAgency(models.Model):
    profession = models.ForeignKey('users.ProfessionProfile', on_delete=models.CASCADE)
    agency = models.ForeignKey(AgencyProfile, on_delete=models.CASCADE)
    request_status = models.BooleanField(default=False)

    def __str__(self):
        return self.request_status



class GigLanguage(models.Model):
    gig = models.ForeignKey(Gig, on_delete=models.CASCADE)
    language = models.CharField(max_length=50)

    def __str__(self):
        return self.gig
    
class GigGallery(models.Model):
    gig = models.ForeignKey(Gig, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profession/gig/')

    def __str__(self):
        return self.gig
    
class GigSelectedLocation(models.Model):
    gig = models.ForeignKey(Gig, on_delete=models.CASCADE)
    location = models.CharField(max_length=50)

    def __str__(self):
        return self.gig