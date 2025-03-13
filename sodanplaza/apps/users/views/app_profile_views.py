from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from apps.users.models import*
from apps.agency.models import*
from apps.users.serializers.app_profile_serializer import *
from classes.response.map_reponse import map_response
from classes.response.generic_response import GenericsRUD,GenericsLC
from rest_framework.exceptions import ValidationError
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from apps.users.serializers.auth_serializer import*
from classes.utils import get_value



class UserProfileView(APIView):
    def post(self,request):
        try:
            user= request.user
            try:
                user_profile= UserProfile.objects.get(id=user.id)
                serializer= UserProfileSerializer(user_profile)
                return map_response(message='User Profile Exists',success=False,data=serializer.data)
            except:
                user_instance= UserProfile.objects.create(user=user,email=user.email)
                serializer= UserProfileSerializer(user_instance)
                delete_profession_profile= ProfessionProfile.objects.filter(user=user.id).delete()
                delete_agency_profile=AgencyProfile.objects.filter(user=user.id).delete()
                return map_response(message='User Profile Created',success=True,data=serializer.data)
        except Exception as e:
            return map_response(message=str(e),success=False)
        

class UserProfileEditView(GenericsRUD):
    permission_classes=[AllowAny]
    model=UserProfile
    serializer_class= UserProfileSerializer
    queryset=UserProfile.objects.all()

    def update(self,request,pk,*args,**kwargs):
        try:
            changeable_user= CustomUser.objects.get(id=pk)
            if not request.user.id== changeable_user.id:
                return map_response(message='Something went wrong',success=False)
            print('----->> Kwargs',kwargs)
            partial= kwargs.get('partial')
            instance= self.get_object()
            print('------>>',instance)
            serializer= self.get_serializer(instance,data=request.data,partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return map_response(message='Data Updated',success=True,data=serializer.data)
        except ValidationError as e:
            return map_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message='Invalid Data',
                error=e.detail,
                success=False
            )
        except Exception as e:
            return map_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message='An unexpected error ocurred',
                error=str(e),
                success=False
                )


class UserProfileListView(GenericsLC):
    model = UserProfile
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all()


class ProfessionProfileView(APIView):

    def post(self,request):
        try:
            user= request.user
            try:
                profession_profile= ProfessionProfile.objects.get(user=user)
                serializer= ProfessionProfileSerializer(profession_profile)
                user_profile= CustomUser.objects.get(id=profession_profile.id)
                user_profile.role= user_profile.Role.PROFESSION
                user_profile.save()
                return map_response(message='Profile Exist',success=True)
            except:
                user_instance= ProfessionProfile.objects.create(user=user,email=user.email)
                serializer= ProfessionProfileSerializer(user_instance)
                agency_profile_delete= AgencyProfile.objects.filter(user=user.id).delete()
                user_profile_delete= UserProfile.objects.filter(user=user.id).delete()
                user_profile.role=user_profile.Role.PROFESSION
                user_profile.save()
                return map_response(message='Profession Profile Created',data=serializer.data,success=True)
        except Exception as e:
            return map_response(message=str(e),success=False)


class ProfessionProfileEditView(GenericsRUD):
    model= ProfessionProfile
    serializer_class=ProfessionProfileSerializer
    queryset=ProfessionProfile.objects.all()

    def update(self,request,pk,*args,**kwargs):
        try:
            changeable_profession= ProfessionProfile.objects.get(id=pk)
            if not request.user.id==changeable_profession.id:
                return map_response(message='Invalid Details',success=False)
            partial= kwargs.get('partial')
            instance=self.get_object()
            serializer= self.get_serializer(instance,data=request.data,partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            agency=get_value(request,key='agency')
            # if agency:
                # request_instance= RequestAttachAgency.objects.create(profession_id=pk,agency_id=int(agency))
            services= request.data.getlist('services[]')
            service_instance_list=[]
            if services:
                ProfessionSelectedService.objects.filter(profession= changeable_profession).delete()

                service_instance=[
                    ProfessionSelectedService.objects.create(
                        service_id= service,
                        profession=changeable_profession
                    ) for service in services
                ]

                ProfessionSelectedService.objects.bulk_create(service_instance)
                service_instance_list=list(
                    SubCategory.objects.filter(id__in=services).values_list('title',flat=True)

                )            
            serializer_copy=serializer.data.copy()
            if len(service_instance_list)>0:
                serializer_copy['service']=service_instance_list
                return map_response(message='Profession Profile Updated',success=True,data=serializer_copy)

            return map_response(message='Profession Profile Updated',success=True,data=serializer_copy)
        except ValidationError as e:
            return map_response(
                message='Invalid Details',
                status_code=status.HTTP_400_BAD_REQUEST,
                error=e.detail,
                success=False
            )
        except Exception as e:
            return map_response(
                message='Unexpected error occured',
                success=False,
                error=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )


        