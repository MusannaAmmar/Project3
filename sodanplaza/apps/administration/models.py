from django.db import models

class VideoTutorial(models.Model):
    title=models.CharField(max_length=500)
    video= models.FileField(upload_to='video/tutorial/')
    duration_seconds= models.PositiveBigIntegerField(default=0)
    duration_minutes=models.PositiveBigIntegerField(default=0)
    duration_hours= models.PositiveBigIntegerField(default=0)
    thumbnail= models.ImageField(upload_to='video/tutorial/tumbnail/',null=True,blank=True)
    user= models.ForeignKey('users.CustomUser',on_delete=models.CASCADE,related_name='users_video')
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    

class Category(models.Model):
    title= models.CharField(max_length=100)
    image= models.ImageField(upload_to='category/image/')
    user=models.ForeignKey('users.CustomUser',on_delete=models.CASCADE,related_name='category_user')
    search_count= models.IntegerField(default=0)

    created_at= models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title

class SubCategory(models.Model):
    category= models.ForeignKey(Category,on_delete=models.CASCADE,related_name='service')
    title= models.CharField(max_length=100,null=True,blank=True)
    image= models.ImageField(upload_to='services/image',null=True,blank=True)
    search_count= models.IntegerField(default=0)

    created_at= models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title


class Language(models.Model):
    name= models.CharField(max_length=100)

    def __str__(self):
        return self.name

class SiteSettings(models.Model):
    site_title= models.CharField(max_length=100)
    site_keywords= models.CharField(max_length=100)
    site_description= models.TextField()
    site_logo=models.ImageField(upload_to='site/images')
    site_hero= models.ImageField(upload_to='site/images')
    site_footer= models.CharField(max_length=100)
    apple_login= models.BooleanField(default=False)
    google_login= models.BooleanField(default=False)
    
    def __str__(self):
        return self.site_title




