from rest_framework.views import APIView
from apps.profession.models import*
from apps.agency.models import*
from apps.users.serializers.app_profile_serializer import*
from apps.profession.serializer.serializers import*
from apps.users.serializers.auth_serializer import*
from classes.response.map_reponse import map_response,get_relative_path
from classes.extra_schema import extra_schema
from rest_framework.pagination import PageNumberPagination
from apps.agency.serializers.profile_serializers import*
from classes.utils import get_value
from django.contrib.auth.hashers import check_password


class GetProfessionDashboardReviewView(APIView):
    def get(self,request):
        try:
            user=request.user
            profession_id= ProfessionProfile.objects.get(user=user)
            profession_serializer= ProfessionProfileSerializer(profession_id)
            reviews= GigReview.objects.filter(profession=profession_id)
            response_data=[]
            for review in reviews:
                review_serializer= GigReviewSerializer(review)
                user_profile= CustomUser.objects.get(id=review.user.id)
                user_profile_serializer= CustomerUserSerializer(user_profile)

                review_data={
                    'review':review_serializer.data,
                    'profession':profession_serializer.data,
                    'user':user_profile_serializer.data
                }
                response_data.append(review_data)

            return map_response(message='Profession Reviews',success=True,data=response_data)
        except Exception as e:
            return map_response(message=str(e),success=False)
        

class ProfessionAddImageView(APIView):
    @extra_schema(
        'AddImage',['images']
    )

    def post(self,request):
        try:
            user=request.user
    
            profession_id=ProfessionProfile.objects.get(user=user).id
            images= request.data.getlist('images[]')
            gig_id= Gig.objects.get(profession=profession_id).id
            count=0
    
            for image in images:
                image_data={
                    'gig':gig_id,
                    'image':image
                }
    
                gallery_serializer= GigSerializer(data=image_data)
                if not gallery_serializer.is_valid():
                    return map_response(message=gallery_serializer.errors,success=False)
                gallery_serializer.save()
                return map_response(message='Images Added',success=True)
        except Exception as e:
            return map_response(message=str(e),success=False)

class ListProfessionImageView(APIView):
    def get(self,request):
        try:
            user= request.user

            profession= ProfessionProfile.objects.get(user=user)

            gig_id=Gig.objects.get(profession=profession).id

            gig_images= GigGallery.objects.filter(gig=gig_id)

            paginator= PageNumberPagination()
            paginator.page_size=12
            paginated_gig_image=paginator.paginate_queryset(gig_images,request)

            gig_image_serializer= GigGallerySerializer(paginated_gig_image,many=True)

            return paginator.get_paginated_response({
                'message':'Profession Images',
                'data':gig_image_serializer.data,
                'success':True
            })
        
        except Exception as e:
            return map_response(message=str(e),success=False)

class ListProfessionDashboardView(APIView):
    def get(self,request):
        try:
            user= request.user
            profession=ProfessionProfile.objects.get(user=user.id)
            gig_id= Gig.objects.filter(profession=profession).id
            gig_services= GigSelectedService.objects.filter(gig=gig_id)
            response_data=[]
            for gig_service in gig_services:
                gig_service_serializer= GigSelectedServiceSerializer(gig_service)
                gig_service_serializer['service_title']=gig_service.service.title
                response_data.append(gig_service_serializer)
            return map_response(message='Profession Services',success=True,data=response_data.data)
        except Exception as e:
            return map_response(message=str(e),success=False)

class ProfessionDashboardStatView(APIView):
    def get(self,request):
        try:
            user=request.user
            # notification= Notification.objects.filter(user=user.id)
            # messages= ChatMessage.objects.filter(receiver=user.id, is_seen=False)
            profession= ProfessionProfile.objects.filter(user=user.id).first()
            if profession:
                gig=Gig.objects.get(profession=profession).first()
                if gig:
                    reviews=GigReview.objects.get(gig=gig).first()
                else:
                    reviews=None
            else:
                reviews=None

            response_data={
                # 'notifications':len(notification)
                # 'message':len(messages)
                'reviews':len(reviews)
            }

            return map_response(message='Professio Dashboard Stats',success=True,data=response_data)
        except Exception as e:
            return map_response(message=str(e),success=False)
        

class ProfessionDashboardAgencyView(APIView):
    def get(self,request):
        try:
            user= request.user
            profession=ProfessionProfile.objects.get(user=user)
            if not profession.agency:
                return map_response(message='Agency Does not Exists',success=False)
            agency= AgencyProfile.objects.get(id=profession.agency.id)
            agency_serializer= AgencyProfileSerializer(agency).data
            if agency.category:
                agency_serializer['category_title']=agency.category.title
            
            #agency owner
            agency_owner= OwnerProfile.objects.filter(agency=agency)
            if agency_owner:
                agency_owner_serializer= OwnerProfileSerializer(agency_owner).data
                agency_serializer['owner']=agency_owner_serializer
            
            agency_services= AgencyServices.objects.filter(agency=agency)
            if agency_services:
                services=[]
                for agency_service in agency_services:
                    agency_service_serializer= AgencyServicesSerializer(agency_service)
                    agency_service_serializer['service_title']=agency_service.service.title
                    services.append(agency_service_serializer)
                agency_serializer['services']=services

            #agency gallery

            agency_gallery=AgencyGallery.objects.filter(agency=agency)
            if agency_gallery:
                agency_gallery_serializer= AgencyGallerySerializer(agency_gallery,many=True)
                agency_serializer['gallery']=agency_gallery_serializer.data

            agency_reviews= AgencyReview.objects.filter(agency=agency)
            if agency_reviews:
                agency_review_serializer= AgencyReviewSerializer(agency_reviews)
                agency_serializer['reviews']=agency_review_serializer.data
            
                agency_employes=AgencyEmploye.objects.filter(agency=agency)
                if agency_employes:
                    employes=[]
                    for agency_employe in agency_employes:
                        agency_employe_serializer= AgencyEmployeSerializer(agency_employe)
                        employe_profile= ProfessionProfile.objects.get(id=agency_employe.id)
                        employe_profile_serializer= ProfessionProfileSerializer(employe_profile)
                        agency_employe_serializer['employe_profile']=employe_profile_serializer.data
                        employes.append(agency_employe_serializer)
                    agency_serializer['employees']=employes
            return map_response(message='Agency Data',success=True,data=agency_serializer)
        except Exception as e:
            return map_response(message=str(e),success=False)
        
class ProfessionSettingView(APIView):
    @extra_schema(
            'professionsetting',['+new_password','current_password','+full_name','+image','+description','+country',
                                 '+state','+city','+pop_up_notification','+chat_notification','+community_notification',
                                 '+tagged_notification','+new_notification','+update_notification']
    )
    def patch(self,request):
        try:
            user=request.user
            new_password= get_value(request,key='new_password')
            current_password=get_value(request,key='current_password')
            full_name=get_value(request,key='full_name')
            image=get_value(request,key='image')
            description=get_value(request,key='description')
            country=get_value(request,key='country')
            state=get_value(request,key='state')
            city=get_value(request,key='city')
            pop_up_notification=get_value(request,key='pop_up_notification')
            chat_notification=get_value(request,key='chat_notification')
            community_notification=get_value(request,key='community_notification')
            tagged_notification=get_value(request,key='tagged_notification')
            new_notification=get_value(request,key='new_notification')
            update_notification=get_value(request,key='update_notification')

            if new_password:
                if check_password(current_password,user.password ):
                    user.set_password(new_password)
                else:
                    return map_response(message='Current Password does not match',success=False)
                user.pop_up_notification=pop_up_notification if pop_up_notification is not None else user.pop_up_notification
                user.chat_notification=chat_notification if chat_notification is not None else user.chat_notification
                user.community_notification=community_notification if community_notification is not None else user.community_notification
                user.tagged_notification=tagged_notification if tagged_notification is not None else user.tagged_notification
                user.new_notification= new_notification if new_notification is not None else user.new_notification
                user.update_notification= update_notification if update_notification is not None else user.update_notification

                user.save()

                profession_instance= ProfessionProfile.objects.get(user=user)

                profession_instance.image=image if image else profession_instance.image
                profession_instance.full_name= full_name if full_name else profession_instance.full_name
                profession_instance.about=description if description else profession_instance.about
                profession_instance.country= country if country else profession_instance.country
                profession_instance.state=state if state else profession_instance.state
                profession_instance.city=city if city else profession_instance.city

                profession_instance.save()

                profession_serializer= ProfessionProfileSerializer(profession_instance).data
                profession_image=profession_serializer['image']
                profession_serializer['image']=get_relative_path(profession_image) if profession_image else None
                profession_logo=profession_serializer['logo']
                profession_serializer['logo']=get_relative_path(profession_logo) if profession_logo else None
                user_serializer= CustomerUserSerializer(user).data
                user_serializer['profession_profile']=profession_serializer
                
                return map_response(message='Data Patched',success=False,data=user_serializer)
        except Exception as e:
            return map_response(message=str(e),success=True)
        

            







