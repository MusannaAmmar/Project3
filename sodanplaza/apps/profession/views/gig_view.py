from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from classes.extra_schema import extra_schema
from classes.utils import get_value
from django.shortcuts import get_object_or_404
from apps.administration.models import Category
from apps.users.models import ProfessionProfile
from apps.profession.models import*
from apps.profession.serializer.serializers import*
from classes.response.map_reponse import map_response
from apps.profession.serializer.serializers import*
import ast
from classes.response.generic_response import GenericsRUD,GenericsLC
from apps.users.serializers.app_profile_serializer import*
from rest_framework import status
from rest_framework.permissions import AllowAny
from uuid import UUID
from django.utils.timezone import now
from datetime import timedelta

class GigView(APIView):
    @extra_schema(
        'Gig',['title','description','is_available','category','skills','locations','languages','faqs','images',
               'meta_title','meta_description','slug']
    )

    def post(self,request):
        try:
            user=request.user
            data=request.data or request.query_params
            category= get_value(request,key='category')
            category_instance= get_object_or_404(Category,id=category)
            profession_instance= get_object_or_404(ProfessionProfile,user=user.id)
            gig_delete= Gig.objects.filter(profession=profession_instance).delete()

            data=data.copy()
            data['category']=category_instance.id
            data['profession']=profession_instance.id

            gig_serializer= GigSerializer(data=data)
            if not gig_serializer.is_valid:
                return map_response(message=gig_serializer.errors,success=False)
            
            gig_instance= gig_serializer.save()
            data['gig']= gig_instance.id

            skills= request.data.getlist('skills[]')
            skills= list(skills) if not isinstance(skills,list) else skills
            for skill in skills:
                skill_instance= get_object_or_404(SubCategory,id=skill)
                skill_data={
                    'skill':skill_instance.id,
                    'gig':gig_instance.id
                }

                selected_skill_serializer= GigSelectedServiceSerializer(data=skill_data)
                if not selected_skill_serializer.is_valid():
                    return map_response(message=selected_skill_serializer.errors,success=False)
                elif selected_skill_serializer.is_valid():
                    selected_skill_serializer.save()
                gig_selected_service=GigSelectedService.objects.filter(gig=gig_instance.id)
                gig_selected_service_serializer= GigSelectedServiceSerializer(gig_selected_service,many=True)

                #languages
                languages= request.query_params.getlist('language[]')
                languages= list(languages) if not isinstance(languages,list) else languages
                for language in languages:
                    language_data={
                        'gig':gig_instance.id,
                        'language':language
                    }

                    selected_language_serializer= GigLanguageSerializer(data=language_data)
                    if not selected_language_serializer.is_valid():
                        return map_response(message=selected_language_serializer.errors,success=False)
                    elif selected_language_serializer.is_valid():
                        selected_language_serializer.save()
                gig_selected_language= GigLanguage.objects.filter(gig=gig_instance.id)
                gig_selected_language_serializer= GigLanguageSerializer(data=gig_selected_language,many=True)

                #locations
                locations= request.query_params.getlist('locations[]')
                locations= list(locations) if not isinstance(locations,list) else locations
                for location in locations:
                    location_data={
                        'gig':gig_instance.id,
                        'location':location
                    }
                    location_select= GigSelectedLocationSerializer(data=location_data)
                    if not location_select.is_valid():
                        return map_response(message=location_select.errors,success=False)
                    elif location_select.is_valid():
                        location_select.save()
                gig_location_select= GigSelectedLocation.objects.filter(gig=gig_instance.id)
                gig_location_select_serializer= GigSelectedLocationSerializer(gig_location_select,many=True)

                #GigFaq

                faqs= request.data.get('faq',[])
                faqs= ast.literal_eval(faqs) if isinstance(faqs,str) else faqs
                faqs= [faqs] if not isinstance(faqs,list) else faqs

                for faq in faqs:
                    faq_data={
                        'questions':faq['questions'],
                        'answer':faq['answer'],
                        'gig':gig_instance.id
                    }

                    faq_serializer= GigFaqSerializer(data=faq_data)
                    if not faq_serializer.is_valid():
                        return map_response(message=faq_serializer.errors,success=False)
                    elif faq_serializer.is_valid():
                        faq_serializer.save()
                gig_faqs= GigFaq.objects.filter(gig=gig_instance.id)
                gig_faq_serializer= GigFaqSerializer(gig_faqs,many=True)

                #Images 
                images= request.data.getlist('images[]')
                for image in images:
                    image_data={
                        'gig':gig_instance.id,
                        'image':image
                    }

                    gallery_serializer= GigGallerySerializer(data=image_data)

                    if not gallery_serializer.is_valid():
                        return map_response(message=gallery_serializer.errors,success=False)
                    elif gallery_serializer.is_valid():
                        gallery_serializer.save()
                image_instance= GigGallery.objects.filter(gig=gig_instance.id)
                image_instance_serializer= GigGallerySerializer(image_instance,many=True)

                response_data={
                    gig_serializer.data,
                    gig_selected_service_serializer.data,
                    gig_selected_language_serializer.data,
                    gig_location_select_serializer.data,
                    gig_faq_serializer.data,
                    image_instance_serializer.data
                    } 
                
            return map_response(message='Gig Created Successfully',data=response_data)
        except Exception as e:
            return map_response(message=str(e),success=False)



class GigEditDeleteView(GenericsRUD):
    model= Gig
    serializer_class=GigSerializer
    queryset= Gig.objects.all()

    @extra_schema(
        'gig',['slug']
    )

    def update(self,request,*args,**kwargs):
        pk=kwargs.get('pk')
        try:
            partial=kwargs.pop('partial')
            profession_profile= ProfessionProfile.objects.get(id=pk)
            profession_profile_serializer= ProfessionProfileSerializer(profession_profile)
            instance= Gig.objects.filter(profession=profession_profile).first()
            serializer= self.get_serializer(instance,data=request.data,partial=partial)
            serializer.is_valid(raise_exceptions=True)
            self.perform_update(serializer)
            serializer_data= dict(serializer.data)

            # Skills Update
            skills= request.data.get('skills',[])
            updated_skills=[]
            if skills:
                for skill in skills:
                    if skill.get('id'):
                        skill_instance= GigSelectedService.objects.filter(id=skill['id'])
                    else:
                        skill_instance= GigSelectedService()
                    skill.pop('skill_title')
                    skill_serializer= GigSelectedServiceSerializer(skill_instance,data=skill,partial=True)
                    if skill_serializer.is_valid():
                        skill_serializer.save()
                        updated_skills.append(skill_serializer)
                    serializer_data['skills']=updated_skills
            # Location Update
            locations= request.data.get('locations',[])
            updated_locations=[]
            if locations:
                for location in locations:
                    if location.get('id'):
                        location_instance= GigSelectedLocation.objects.filter(id=location['id'])
                    else:
                        location_instance=GigSelectedLocation()
                    location_instance_serializer= GigSelectedLocationSerializer(location_instance,data=location,partial=True)
                    if location_instance_serializer.is_valid():
                        location_instance_serializer.save()
                updated_locations.append(location_instance_serializer)
                serializer_data['location']=updated_locations
            # Faq Update
            faqs= request.data.get('faqs',[])
            updated_faq=[]
            if faqs:
                for faq in faqs:
                    if faq.get('id'):
                        faq_instance= GigFaq.objects.get(id=faq['id'])
                    else:
                        faq_instance= GigFaq()
                    faq_instance_serializer= GigFaqSerializer(faq_instance,data=faq,partial=True)
                    if faq_instance_serializer.is_valid():
                        faq_instance_serializer.save()
                    updated_faq.append(faq_instance_serializer)
                serializer_data['faqs']=updated_faq
            # Image Update
            images= request.data.get('images',[])
            updated_images=[]
            if images:
                for image in images:
                    if image.get('id'):
                        image_instance= GigGallery.objects.get(id=image['id'])
                    else:
                        image_instance=GigGallery()
                    image_instance_serializer=GigGallerySerializer(image_instance,data=image,partial=True)
                    if image_instance_serializer.is_valid():
                        image_instance_serializer.save()
                    updated_images.append(image_instance_serializer)
                serializer_data['images']=updated_images
            # Language Update
            languages= request.data.get('language',[])
            updated_language=[]
            if language:
                for language in languages:
                    if language:
                        language_instance=GigLanguage.objects.get(id=language['id'])
                    else:
                        language_instance=GigLanguage()
                    language_instance_serializer= GigLanguageSerializer(language_instance,data=language,partial=True)
                    if language_instance_serializer.is_valid():
                        language_instance_serializer.save()
                    updated_language.append(language_instance_serializer)
                serializer_data['language']=updated_language
            return map_response(message='Data Updated',success=True,data=serializer_data)
        except ValidationError as e:
            return map_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message='Invalid Data',
                error=e.detail,
                success=False
            )
        except Exception as e:
            return map_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message='Something went wrong',
                error=str(e),
                success=False
            )
        
    def retrieve(self,request,*args,**kwargs):
        pk=kwargs.get('pk')
        try:
            slug=get_value(request,key='slug')
            profession_profile=ProfessionProfile.objects.get(id=pk)
            profession_profile_serializer= ProfessionProfileSerializer(profession_profile)
            instance= Gig.objects.filter(profession=profession_profile).last()
            serializer= self.get_serializer(instance)
            images=[]
            skills=[]
            locations=[]
            faqs=[]
            reviews=[]
            languages=[]

            gig_gallery=GigGallery.objects.filter(gig=instance)
            for image in gig_gallery:
                image_serializer=GigGallerySerializer(image).data
                image_url=image_serializer['image']

                if not image_url.startswith('media/profession/gig/'):
                    split_url= image_url.split('/')[-1]
                    image_url=f'/media/profession/gig/{split_url}'
                    image_serializer['image']=image_url

                images.append(image_serializer)
            gig_skills=GigSelectedService.objects.filter(gig=instance)
            for skill in gig_skills:
                skill_serializer= GigSelectedServiceSerializer(skill).data
                skill_serializer['skill_title']=skill.service.title
                skills.append(skill_serializer)
            gig_location= GigSelectedLocation.objects.filter(gig=instance)
            for location in gig_location:
                location_serializer= GigSelectedLocationSerializer(location).data
                locations.append(location_serializer)
            
            gig_faqs= Gig.objects.filter(gig=instance.id)
            for faq in gig_faqs:
                faq_data=GigSerializer(faq).data
                faqs.append(faq_data)

            gig_review= GigReview.objects.filter(gig=instance)
            for review in gig_review:
                image= review.user.image
                if not image:
                    data={
                        'review':review.comment,
                        'ratings':review.rating,
                        'created_at':review.created_at,
                        'first_name':review.user.first_name,
                        'last_name':review.user.last_name,
                        'image':image.urls

                    }
                else:
                    data={
                        'review':review.comment,
                        'ratings':review.rating,
                        'created_at':review.created_at,
                        'first_name':review.user.first_name,
                        'last_name':review.user.last_name,
                        'image':image.urls

                    }
                reviews.append(data)
            gig_language= GigLanguage.objects.filter(gig=instance)
            for language in gig_language:
                gig_language_serializer= GigLanguageSerializer(language).data
                languages.append(gig_language_serializer)
            
            serializer_copy= serializer.data
            serializer_copy['images']=images
            serializer_copy['skills']=skills
            serializer_copy['locations']=locations
            serializer_copy['faqs']=faqs
            serializer_copy['reviews']=reviews
            serializer_copy['languages']=languages
            serializer_copy['category_title']=instance.category.title
            serializer_copy['profession_profile']=profession_profile_serializer.data

            return map_response(message='Data Retrieved',data=serializer_copy,success=True)
        except Exception as e:
            return map_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message='Internal Error',
                error=str(e),
                success=False
            )
        
class GetGigbySlugView(GenericsRUD):
    permission_classes=[AllowAny]
    serializer_class= GigSerializer
    model= Gig
    queryset=Gig.objects.all()

    @extra_schema(
        'Gig',['slug']
    )

    def retrieve(self,request,*args,**kwargs):
        try:
            slug=kwargs.get('pk')
            instance=Gig.objects.filter(slug=slug).last()
            if instance.is_publish==False:
                return map_response(message='Gig is not Published',success=False)
            serializer=self.get_serializer(instance)
            profession=instance.profession
            profession_serializer= ProfessionProfileSerializer(profession)
            images=[]
            skills=[]
            locations=[]
            faqs=[]
            reviews=[]
            languages=[]

            gig_gallery= GigGallery.objects.filter(gig=instance.id)
            for image in gig_gallery:
                images.append(image.image.url)

            gig_skills=GigSelectedService.objects.filter(gig=instance.id)
            for skill in gig_skills:
                skills.append(skill.service.title)

            gig_location= GigSelectedLocation.objects.filter(gig=instance.id)
            for location in gig_location:
                locations.append(location.location)
            
            gig_faqs= GigFaq.objects.filter(gig=instance.id)
            for faq in gig_faqs:
                data={
                    'question':faq.question,
                    'answer':faq.answer
                }
                faqs.append(data)
            gig_reviews= GigReview.objects.filter(gig=instance.id)
            for review in gig_reviews:
                data={
                    'reviews':review.comment,
                    'ratings':review.rating,
                    'created_at':review.created_at,
                    'first_name':review.user.first_name,
                    'last_name':review.user.last_name,
                    'image':review.user.image if review.user.image else None
                }

                reviews.append(data)

            gig_languages= GigLanguage.objects.filter(gig=instance.id)
            for language in gig_languages:
                languages.append(language)
            serializer_copy=serializer.data
            serializer_copy['images']=images
            serializer_copy['skills']=skills
            serializer_copy['locations']=locations
            serializer_copy['faqs']=faqs
            serializer_copy['reviews']=reviews
            serializer_copy['languages']=languages
            serializer_copy['category_title']=instance.category.title
            serializer_copy['profession_profile']=profession_serializer.data

            return map_response(message='Data Retrieved',success=True,data=serializer_copy)
        except Exception as e:
            return map_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message='Invalid Server error',
                error=str(e),
                success=False
            )
        
class GigListViewApp(GenericsLC):
    permission_classes=[AllowAny]

    def list(self,request):
        try:
            gigs=Gig.objects.filter(is_publish=True)
            response_data=[]
            for gig in gigs:
                gig_serializer= GigSerializer(gig)
                gig_serializer_copy= gig_serializer.data.copy()
                gig_serializer_copy['category']=gig.category.title
                gig_serializer_copy['profession']=gig.profession.first_name

                gig_selected_skill= GigSelectedService.objects.filter(gig= gig.id)
                gig_selected_skill_serializer= GigSelectedServiceSerializer(gig_selected_skill,many=True)
                for index in gig_selected_skill_serializer.data:
                    skill=SubCategory.objects.get(id=index['skill'])
                    index['skill']=skill.title
                gig_selected_location=GigSelectedLocation.objects.filter(gig=gig.id)
                gig_selected_location_serializer=GigSelectedLocationSerializer(gig_selected_location,many=True)

                gig_reviews= GigReview.objects.filter(gig=gig.id)
                gig_reviews_serializer= GigReviewSerializer(gig_reviews,many=True)

                gig_faqs= GigFaq.objects.filter(gig=gig.id)
                gig_faq_serializer= GigFaqSerializer(gig_faqs, many=True)

                gig_gallery= GigGallery.objects.filter(gig=gig.id)
                gig_gallery_serializer= GigGallerySerializer(gig_gallery,many=True)

                profession= ProfessionProfile.objects.filter(gig=gig.id)
                profession_serializer= ProfessionProfileSerializer(profession)

                gig_serializer_copy['profession_profile']= profession_serializer.data
                gig_serializer_copy['skills']= gig_selected_skill_serializer.data
                gig_serializer_copy['location']=gig_selected_location_serializer.data
                gig_serializer_copy['reviews']=gig_reviews_serializer.data
                gig_serializer_copy['faq']=gig_faq_serializer.data
                gig_serializer_copy['images']=gig_gallery_serializer.data
                gig_serializer_copy['jobs']= len(gig_reviews_serializer.data)

                response_data.append(gig_serializer_copy)
            return map_response(message='Gig Lists',success=True,data=response_data)
        except Exception as e:
            return map_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message='Internal Error',
                error=str(e),
                success=False
            )

# Gig CRUD
class GigSkillEditUpdateDeleteView(GenericsRUD):
    model= GigSelectedService
    serializer_class= GigSelectedServiceSerializer
    queryset=GigSelectedService.objects.all()


class GigSkillListView(GenericsLC):
    model= GigSelectedService
    serializer_class= GigSelectedServiceSerializer
    queryset= GigSelectedService.objects.all()

# Gallery CRUD

class GigGalleryEditDeleteUpdateView(GenericsRUD):
    model= GigGallery
    serializer_class= GigGallerySerializer
    queryset= GigGallery.objects.all()


class GigGalleryListView(GenericsLC):
    model= GigGallery
    serializer_class= GigGallerySerializer
    queryset= GigGallery.objects.all()

#Gig Locations CRUD

class GigLocationEditDeleteUpdateView(GenericsRUD):
    model= GigSelectedLocation
    serializer_class= GigSelectedLocationSerializer
    queryset=GigLanguage.objects.all()

class GigLocationListView(GenericsLC):
    model= GigSelectedLocation
    serializer_class=GigSelectedLocationSerializer
    queryset= GigSelectedLocation.objects.all()

#Gig Faq CRUD

class GigSkillEditDeleteUpdateView(GenericsRUD):
    model= GigFaq
    serializer_class= GigFaqSerializer
    queryset=GigFaq.objects.all()

class GigSkillListView(GenericsLC):
    model= GigFaq
    serializer_class= GigFaqSerializer
    queryset= GigFaq.objects.all()

class GigReviewView(APIView):
    @extra_schema(
        'Reviews',['qr_code','review',' ratings','gig_id']
    )

    def post(self,request):
        try:
            user=request.user
            user_profile= UserProfile.objects.get(user_id=user.id)
            qr_code= get_value(request,key='qr_code')
            input_qr_code= UUID(qr_code)
            review= get_value(request,key='review')
            ratings=get_value(request,key='ratings')
            gig_id= get_value(request,key='gig_id')

            gig_instance= get_object_or_404(Gig,id=gig_id)
            user_qr_code=gig_instance.profession.user.qr_code
            user_qr_code_created_at= gig_instance.profession.user.qr_code_created_at

            # Validate QR code
            if not input_qr_code==user_qr_code:
                return map_response(message={'error:Invalid QR code'},success=False)
            if now()- user_qr_code_created_at>timedelta(minutes=5):
                return map_response(message='QR code expired',success=False)
            
            today= now().date()
            if GigReview.objects.filter(user=user.id,gig=gig_instance.id,created_at=today).exists():
                return map_response(message={'error:You have already reviewed this gig today'},success=False)
            
            review_data={
                'review':review,
                'ratings':ratings,
                'gig':gig_instance.id,
                'user':user_profile.id,
                'profession':gig_instance.profession.id                
                
                }
            review_serializer= GigReviewSerializer(data=review_data)
            if not review_serializer.is_valid():
                return map_response(message=review_serializer.errors,success=False)
            review_serializer.save()

            user_qr_code=None
            user_qr_code_created_at=None
            user.save()

            #Profession ratings

            new_ratings= gig_instance.profession
            new_ratings.jobs_count+=1
            new_ratings.ratings_count+=1
            new_ratings.sum_ratings+=int(ratings)

            if int(ratings) == 1:
                new_ratings.one_star += 1
            elif int(ratings) == 2:
                new_ratings.two_star += 1
            elif int(ratings) == 3:
                new_ratings.three_star += 1
            elif int(ratings) == 4:
                new_ratings.four_star += 1
            elif int(ratings) == 5:
                new_ratings.five_star += 1

            new_ratings.ratings=(new_ratings.sum_ratings)/(new_ratings.ratings_count)
            gig_instance.save()
            new_ratings.save()
            return map_response(message='Review Submitted',success=True,data=review_serializer.data)
        except Exception as e:
            return map_response(message=str(e),success=False)


















        













                            








































