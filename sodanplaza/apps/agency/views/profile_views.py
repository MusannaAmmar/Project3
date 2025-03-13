from django.shortcuts import render
from rest_framework.views import APIView
from apps.agency.models import*
from apps.agency.serializers.profile_serializers import *
from apps.users.serializers.app_profile_serializer import*
from classes.response.map_reponse import map_response
from classes.response.generic_response import GenericsRUD,GenericsLC
from django.shortcuts import get_object_or_404
from classes.utils import get_value
from rest_framework.exceptions import ValidationError
from rest_framework import status
from classes.response.map_reponse import get_relative_path
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from classes.extra_schema import extra_schema
from uuid import UUID
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from datetime import timedelta
from drf_spectacular.utils import extend_schema,OpenApiParameter


class AgencyProfileView(APIView):
    def post(self,request):
        try:
            user= request.user
            try:
                agency_profile= AgencyProfile.objects.get(user=user.id)
                agency_profile_serializer= AgencyProfileSerializer(agency_profile)

                user_profile= CustomUser.objects.get(id=user.id)
                user_profile.role= user_profile.Role.AGENCY
                return map_response(message='Profile Exist',success=True,data=agency_profile_serializer.data)
            except Exception as e:
                print(str(e))
                user_instance= AgencyProfile.objects.create(user=user)
                serializer= AgencyProfileSerializer(user_instance)

                user_profile= CustomUser.objects.get(id=user.id)

                delete_user_profile=UserProfile.objects.filter(user=user.id).delete()
                delete_profession=ProfessionProfile.objects.filter(user=user.id).delete()

                user_profile.role= user_profile.Role.AGENCY
                user_profile.save()
                return map_response(message='User Profile Created',success=True,data=serializer.data)
        except Exception as e:
            return map_response(message=str(e),success=False)

        
class EditAgencyProfileView(GenericsRUD):
    model= AgencyProfile
    serializer_class=AgencyProfileSerializer
    queryset= AgencyProfile.objects.all()

    def update(self,request,pk,*args,**kwargs):
        try:
            changeable_agency= AgencyProfile.objects.get(id=pk)
            if not request.user.id== changeable_agency.id:
                return map_response(message='Something went wrong',success=False)
            partial= kwargs.pop('partial',False)
            instance= self.get_object()
            slug= request.data['business_name'].replace(' ','-') if request.data.get('business_name',None) else None
            data= request.data
            data['slug']=slug
            serializer= self.get_serializer(instance,partial,data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            serializer_copy= dict(serializer.data).copy()
            if instance.category:
                serializer_copy['category_title']=instance.category.data

            owner_name= get_value(request,key='owner_name')
            owner_email= get_value(request,key='owner_email')
            owner_contact= get_value(request,key='owner_contact')
            agency= instance.id
            agency_owner= OwnerProfile.objects.filter(agency=agency).first()
            if not agency_owner:
                if owner_name and owner_email and owner_contact:
                    owner_data={
                        'owner_name':owner_name,
                        'owner_email':owner_email,
                        'owner_contact':owner_contact,
                        'agency':agency
                    }

                    owner_serializer= OwnerProfileSerializer(data=owner_data)
                    if not owner_serializer.is_valid():
                        return map_response(message=owner_serializer.errors,success=False)
                    owner_serializer.save()
                    serializer_copy['owner']= owner_serializer.data

            services= request.data.get('services',[])
            services_list= []
            if services:
                AgencyServices.objects.filter(agency=changeable_agency).delete()

                for service in service:
                    service_instance= AgencyServices.objects.create(
                        agency=changeable_agency,service_id= service

                    )

                    service_serializer= AgencyServicesSerializer(service_instance)
                    services_list.append(service_serializer.data)
                    serializer_copy['services']=services_list

            return map_response(message='Data Updated',success=True,data=serializer_copy)
        except ValidationError as e:
            return map_response(
                message='Invalid Data',
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False,
                error=e.detail
            )
        except Exception as e:
            return map_response(
                message='Internal server error',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error=str(e),
                success=False
            )
        

    def retrieve(self,request,*args,**kwargs):
        try:
            instance=self.get_object()
            serializer= self.get_serializer(instance)
            data=serializer.data
            data['category_title']= instance.category.title
            services= AgencyServices.objects.filter(agency=instance)
            services_list=[]
            for service in services:
                service_serializer= AgencyServicesSerializer(service)
                serializer_data=service_serializer.data
                serializer_data['service_title']= service.service.title
                services_list.append(serializer_data)

            data['services']=services_list

            gallery= AgencyGallery.objects.filter(agency=instance)
            gallery=[]
            for image in gallery:
                image_serializer= AgencyGallerySerializer(image).data
                gallery.append(image_serializer)
            data['image']=gallery if gallery else []
            return map_response(message='Data Retrieved',success=True,data=data)
        except Exception as e:
            return map_response(message='Something went wrong',success=False,error=str(e))
        

class AgencyProfileSlugView(APIView):

    def get(self,request,pk,*args,**kwargs):
        try:
            slug=pk

            instance= AgencyProfile.objects.filter(slug=slug).last()
            instance_serializer= AgencyProfileSerializer(instance)
            data=instance_serializer.data
            data['category_title']= instance.category.title

            services= AgencyServices.objects.filter(agency= instance)
            services_list=[]
            for service in services:
                service_serializer= AgencyProfileSerializer(service)
                serialized_data=service_serializer.data
                serialized_data['service']= service.service.title
                services_list.append(serialized_data)
            data['service']=services_list

            gallery= AgencyGallery.objects.filter(agency=instance)
            gallery=[]
            for images in gallery:
                image_serializer=AgencyGallerySerializer(images)
                image_data=image_serializer.data
                gallery.append(image_data)

            data['images']=gallery if gallery else []
            return map_response(message='Data retrived',success=True,data=data)
        except Exception as e:
            return map_response(message='something went wrong',error=str(e),success=False)

class AgencyProfileEditViewApp(GenericsRUD):
    model= AgencyProfile
    serializer_class= AgencyProfileSerializer
    queryset= AgencyProfile.objects.all()


    def update(self,request,pk,*args,**kwargs):
        try:
            changeable_agency= AgencyProfile.objects.get(id=pk)
            if not request.user.id==changeable_agency.user.id:
                return map_response(message='Agency does not exist',success=False)
            partial= partial.pop('partial')
            instance= self.get_object()
            serializer= self.get_serializer(instance,partial=True,data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            serializer_copy=dict(serializer.data).copy()
            if instance.category:
                serializer_copy['category_title']=  instance.category.title
            #owner_name

            owner_name= get_value(request,key='owner_name')
            owner_email= get_value(request,key='owner_email')
            owner_contact= get_value(request,key='owner_contact')
            agency=instance.id
            agency_owner= OwnerProfile.objects.filter(agency=agency).first()
            if not agency_owner:
                if owner_name and owner_email and owner_contact:
                    owner_data={
                        'owner_name':owner_name,
                        'owner_email':owner_email,
                        'owner_contact':owner_contact,
                        'agency':agency
                    }
                    owner_serializer=OwnerProfileSerializer(owner_data)
                    if not owner_serializer.is_valid():
                        return map_response(message=owner_serializer.errors,success=False)
                    
                    serializer_copy['owner']= owner_serializer.data

            #services 
            services= request.data.get('services' ,[])
            services_list=[]
            AgencyServices.objects.filter(agency=changeable_agency.id).delete()

            for service in services:
                service_instance= AgencyServices.objects.create(
                    agency=changeable_agency.id,
                    service_id=service
                )
                serializer_data= AgencyServicesSerializer(service_instance)
                services_list.append(serializer_data.data)
            serializer_copy['services']= services_list

            return map_response(message='Data Updated',success=True)

        except ValidationError as e:
            return map_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                error=e.detail,
                message='Invalid Data',
                success=False
            )
    
    def retrieve(self,request,*args,**kwargs):
        try:
            instance= self.get_object()
            serializer= self.get_serializer(instance)
            data=serializer.data
            logo=data['logo']
            certificate_image= data['certificate_image']
            data['logo']= get_relative_path(logo) if logo else None
            data['certificate_image']=get_relative_path(certificate_image) if certificate_image else None
            data['cateogory_title']= instance.category.title

            services= AgencyServices.objects.filter(agency=instance).first()
            services_list=[]

            for service in services:
                services_serializer= AgencyServicesSerializer(service)
                serialized_data= services_serializer.data
                serialized_data['services_title']= service.service.title
                services_list.append(serialized_data)
            data['services']= services_list

            #gallery
            image_gallery= AgencyGallery.objects.filter(agency=instance).first()
            image_gallery=[]
            for images in image_gallery:
                serialized_data=AgencyGallerySerializer(images).data
                image= serialized_data['image']
                serialized_data['image']=get_relative_path(image)
                image_gallery.append(serialized_data)

            data['images']= image_gallery if image_gallery else None
            return map_response(message='Data Retrieved', success=True,data=data)
        except Exception as e:
            return map_response(message=str(e),success=False,)




class AgencyProfileListView(APIView):
    permission_classes= [AllowAny]

    def get(self,request,*args,**kwargs):
        try:
            agencies= AgencyProfile.objects.all()
            paginator= PageNumberPagination()
            paginator.page_size= 10
            paginated_agencies=paginator.paginate_queryset(agencies,request)
            agency_profile= []
            for agency_instance in paginated_agencies:
                agency_serializer= AgencyProfileSerializer(agency_instance).data
                if agency_instance.category:
                    agency_serializer['category_title']= agency_instance.category.title
                
                agency_owner= OwnerProfile.objects.filter(agency= agency_instance)
                if agency_owner.exists():
                    agency_owner_serializer= OwnerProfileSerializer(agency_owner).data
                    agency_serializer['owner']=agency_owner_serializer

                #services
                agency_services= AgencyServices.objects.filter(agency=agency_instance)
                if agency_services.exists():
                    services=[]
                    for service in services:
                        service_serializer= AgencyServicesSerializer(service).data
                        service_serializer['service_title']= agency_services.service.title
                        services.append(service_serializer)
                    agency_serializer['services']= services
                
                #gallery
                agency_gallery= AgencyGallery.objects.filter(agency=agency_instance)
                if agency_gallery.exists():
                    agency_gallery_serializer= AgencyServicesSerializer(agency_gallery)
                    agency_serializer['gallery']= agency_gallery_serializer.data

                agency_reviews= AgencyReview.objects.filter(agency=agency_instance)
                if agency_reviews.exists():
                    agency_review_serializer= AgencyReviewSerializer(agency_reviews)
                    agency_serializer['reviews']=agency_review_serializer.data
                
                #employes
                agency_employes= AgencyEmploye.objects.filter(agency=agency_instance)
                if agency_employes.exists():
                    employees=[]
                    for agency_employee in agency_employes:
                        agency_employe_serializer= AgencyEmployeSerializer(agency_employee).data
                        employee_profile= ProfessionProfile.objects.get(id=agency_employee.id)
                        employee_serializer= ProfessionProfileSerializer(employee_profile).data
                        agency_employe_serializer['employee_profile']=employee_serializer
                        employees.append(agency_employe_serializer)
                    agency_serializer['employees']=employees
                agency_profile.append(agency_serializer)

                #agency reviews
               
                
                paginated_response= paginator.get_paginated_response(agency_profile).data
                return map_response(
                    message='Agency Data',
                    data=paginated_response,
                    success=True
                )
            
        except Exception as e:
            return map_response(
                message='Something went wrong',
                error=str(e),
                success=False
            )

class AgencyOwnerEditDeleteView(GenericsRUD):
    model=OwnerProfile
    queryset= OwnerProfile.objects.all()
    serializer_class=OwnerProfileSerializer

class AgencyOwnerListView(GenericsLC):
    model= OwnerProfile
    queryset=OwnerProfile.objects.all()
    serializer_class=OwnerProfileSerializer

class SelectedServiceEditDeleteView(GenericsRUD):
    model=AgencyServices
    queryset= AgencyServices.objects.all()
    serializer_class= AgencyServicesSerializer

class SelectedServiceListView(GenericsLC):
    model=AgencyServices
    queryset= AgencyServices.objects.all()
    serializer_class= AgencyServicesSerializer


    def list(self,request,*args,**kwargs):
        try:
            user=request.user
            agency= AgencyProfile.objects.get(user=user)
            services_instance= AgencyServices.objects.filter(agency=agency)

            #initialize pagination
            paginator=PageNumberPagination
            paginator.page_size=10
            paginated_queryset=paginator.paginate_queryset(services_instance,request)

            services_list=[]
            for services in paginated_queryset:
                serialized_data=AgencyServicesSerializer(services).data
                serialized_data['services_title']=services.service.title
                services_list.append(serialized_data)

            paginated_response=paginator.get_paginated_response(services_list).data

            return map_response(
                message='List is generated',
                data=paginated_response,
                success=True
            )
        except Exception as e:
            return map_response(
                message=str(e),
                success=False
            )


class AgencyReviewView(APIView):
    @extra_schema(
        'Reviews',['qr_code','reviews','ratings',' agency_id']
        
    )

    def post(self,request):
        try:
            user=request.user
            user_profile=UserProfile.objects.get(user_id=user.id)
            qr_code=get_value(request,key='qr_code')
            input_qr_code=UUID(qr_code)
            review=get_value(request,key='reviews')
            ratings=get_value(request,key='ratings')
            agency_id= get_value(request,key='agency_id')

            agency_instance= get_object_or_404(AgencyProfile,id=agency_id)
            user_qr_code= agency_instance.user.qr_code
            user_qr_code_created_at=agency_instance.user.qr_code_created_at

            if not input_qr_code==user_qr_code:
                return map_response(message='Invalid QR code',success=False)
            if now() -user_qr_code_created_at > timedelta(minutes=5):
                return map_response(message={'error':'QR code expired'},success=False)
            today=now().data()
            if AgencyReview.objects.filter(user=user_profile.id,agency=agency_instance.id,
                                          created_at_date=today ).exists():
                return map_response(message={'error: You already reviewed this gig'},success=False)
            
            review_data={
                'review':review,
                'ratings':ratings,
                'agency':agency_instance.id,
                'user':user_profile.id
            }

            review_serializer= AgencyReviewSerializer(data=review_data)
            if not review_serializer.is_valid():
                return map_response(message=review_serializer.errors,success=False)
            review_serializer.save()

            user_qr_code=None
            user_qr_code_created_at=None
            user.save()

            new_ratings=agency_instance
            new_ratings.jobs_count+=1
            new_ratings.rating_count+=1
            new_ratings.sum_rating+= int(ratings)

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

            new_ratings.ratings=new_ratings.sum_rating/new_ratings.rating_count

            return map_response(
                message='Review Submitted succesfully',
                success=True,
                data=review_serializer.data
            )
        except Exception as e:
            return map_response(message=str(e),success=False)









                











                









    





























