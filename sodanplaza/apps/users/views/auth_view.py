from rest_framework.views import APIView
from classes.extra_schema import extra_schema
from classes.utils import get_value
from apps.users.models import*
from classes.response.map_reponse import map_response
from apps.users.serializers.auth_serializer import*
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404,render
from django.contrib.auth import authenticate
from apps.agency.models import *
from apps.agency.serializers.profile_serializers import*
from apps.users.serializers.app_profile_serializer import*
from classes.response.map_reponse import get_relative_path
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny



class Register(APIView):
    permission_classes=[AllowAny]

    @extra_schema(
            'Register',['email','password']
    )

    def post(self,request):

        email= get_value(request,key='email')
        password=get_value(request,key='password')

        try:
            existing_user= CustomUser.objects.get(email=email)
            if existing_user:
                if existing_user.is_deleted :
                    existing_user.is_deleted=False
                    existing_user.save()
                    serializer= CustomerUserSerializer(existing_user)
                    return map_response(message='User Retrieved',success=True,data=serializer.data)
                else:
                    return map_response(message='User Exists',success=False)
        except ObjectDoesNotExist:
            data={
                'email':email,
                'password':password
            }

            serializer=CustomerUserSerializer(data=data)
            if serializer.is_valid():
                user=serializer.save()
                user.generate_otp()
                return map_response(message='Otp Send to your email',success=True,)
            return map_response(message=serializer.errors,success=False)
        except Exception as e:
            return map_response(message=str(e),success=False)

class DeleteRegister(APIView):
    permission_classes=[AllowAny]

    def delete(self,request,pk):
        try:
            user=CustomUser.objects.get(pk=pk)
            user.delete()
            return map_response('User deleted')
        except Exception as e:
            return map_response(message=str(e),success=False)


class LoginView(APIView):
    permission_classes=[AllowAny]
    @extra_schema(
        'Login',['email','password']
    )

    def post(self,request):
        try:
            email=get_value(request,key='email')
            password=get_value(request,key='password')
    
    
            user_existance= get_object_or_404(CustomUser,email=email)
    
            if not user_existance.is_active:
                return map_response(message='OTP not verified',success=False)
            user= authenticate(request,email=email,password=password)
            print('---->>',password)
            print('---->>',user_existance.is_active)

    

            if not user:
                return map_response(message='Invalid Credentials',success=False)
            serializer= CustomerUserSerializer(user)
            refresh=RefreshToken.for_user(user)    
            response_data={
                'user':serializer.data,
                'refresh':str(refresh),
                'access':str(refresh.access_token)
            }

            role=user.role
            print('----->>',role)

            profile_mapping={
                user.Role.AGENCY:(AgencyProfile,AgencyProfileSerializer),
                user.Role.PROFESSION: (ProfessionProfile, ProfessionProfileSerializer),
                user.Role.USER:(UserProfile,UserProfileSerializer),
            }

            if role in profile_mapping:
                profile_model,serializer_class= profile_mapping[role]
                try:
                    profile=profile_model.objects.get(user=user)
                    serializer=serializer_class(profile)
                    profile_data=serializer.data
                    print('--->>',profile_data)

                    if role==user.Role.AGENCY:
                        services= AgencyServices.objects.get(agency=profile.id)
                        service_serializer=AgencyServicesSerializer(services,many=True)
                        profile_data['services']=service_serializer.data
                    elif role==user.Role.PROFESSION:
                        image= profile_data['image']
                        print('image--->>',image)
                        profile_data['image']=get_relative_path(image) if image else None
                        logo= profile_data['logo']
                        profile_data['logo']=get_relative_path(logo) if logo else None
                        services= ProfessionSelectedService.objects.filter(profession=profile.id)
                        services_list=[]
                        for service in services:
                            service_serializer= ProfessionSelectedServiceSerializer(service).data
                            service_title= service.service.title
                            service_serializer['service_title']=service_title
                            services_list.append(service_serializer)
                        profile_data['service']=services_list

                        if hasattr(profile,'category') and profile.category:
                            profile_data['category_title']=profile.category.title

                        response_data['profile_data']=profile_data
                except profile_model.DoesNotExist:
                    response_data['profile_data']=None
                return map_response(message='Login Successfull',success=True,data=response_data)
            elif user.role==CustomUser.Role.ADMIN:
                return map_response(message='Login Successfull',success=True,data=response_data)
            return map_response(message='Invalid Role',success=False)
        except Exception as e:
            return map_response(message=str(e),success=False)

class VerifyOTPView(APIView):
    permission_classes=[AllowAny]
    @extra_schema(
        'OTPVerification',['email','otp']
    )

    def post(self,request):
        try:
            email= get_value(request,key='email')
            otp=get_value(request,key='otp')
    
            if not otp or not email:
                return map_response(message='otp and email is required',success=False)
        
            user= CustomUser.objects.get(email=email,is_deleted=False)
            if not user:
                return map_response(message='email is not valid',success=False)
            if user.verify_otp(otp):
                data=CustomerUserSerializer(user).data
                refresh=RefreshToken.for_user(user)
                response_data={
                        'user':data,
                        'refresh':str(refresh),
                        'access':str(refresh.access_token)
                    }
                user.is_active=True
                user.save()
                role=user.role

                profile_mapping={
                    user.Role.AGENCY:(AgencyProfile,AgencyProfileSerializer),
                    user.Role.PROFESSION:(ProfessionProfile,ProfessionProfileSerializer),
                    user.Role.USER:(UserProfile,UserProfileSerializer)
                }

                if role in profile_mapping:
                    profile_model,serializer_class= profile_mapping[role]
                    try:
                        profile= profile_model.objects.get(user=user)
                        profile_data=serializer_class(profile).data
                        if role==user.Role.AGENCY:
                            services= AgencyServices.objects.filter(agency=profile.id)
                            service_serializer= AgencyServicesSerializer(services,many=True)
                            profile_data['services']=service_serializer.data

                        elif role==user.Role.PROFESSION:
                            services= ProfessionSelectedService.objects.filter(profession=profile.id)
                            service_list=[]
                            for service in services:
                                service_serializer= ProfessionSelectedServiceSerializer(service).data
                                service_title=service.service.title
                                service_serializer['service_title']=service_title
                                service_list.append(service_serializer)
                            profile_data['services']=service_list

                        if hasattr(profile,'category') and profile.category:
                            profile_data['catgeory_title']=profile.category.title

                        response_data[  'profile_data']=profile_data
                    except profile_model.DoesNotExist:
                        response_data['profile_data'] = None
                    return map_response(message='Login Successfull',success=True,data=response_data)
                elif user.role== user.Role.ADMIN:
                    return map_response(message='Login Successfull',success=True,data=response_data)
                return map_response(message='Invalid Role',success=False)
            return map_response(message='OTP verification failed',success=False)
        except Exception as e:
            return map_response(message=str(e),success=False)


class ForgotPasswordView(APIView):
    permission_classes=[AllowAny]
    @extra_schema(
        'Forgot',['email']
    )


    def post(self,request):
        try:
            serializer= ForgotPasswordSerializer(data=request.data or request.query_params)
            print('----->>',serializer)
            if serializer.is_valid():
                user=serializer.save()
                return map_response(message=f'OTP has been send to your email {user.email}'
                ,success=True,data=serializer.data)
        except Exception as e:
            return map_response(message=str(e),success=False)



class SetPassword(APIView):
    permission_classes=[AllowAny]
    @extra_schema(
        'SetPassword',['email','otp','password']
    )


    def post(self,request):
        try:
            email= get_value(request,key='email')
            password= get_value(request,key='password')
            otp= get_value(request,key='otp')
    
    
            if not email or not otp:
                return map_response(message='Authorization details required',success=False)
            elif not password:
                return map_response(message='New password required',success=False)
            
            user= get_object_or_404(CustomUser,email=email)
            if not user:
                return map_response(message='Invalid User',success=False)
            if user.verify_otp(otp):
                user.password=password
                user.save()
                serializer=CustomerUserSerializer(user)
                return map_response(message='Password changed',success=True,data=serializer.data)
            return map_response(message='Incorrect OTP or expired',success=False)
        except Exception as e:
            return map_response(message=str(e),success=False)
    

class GetUserView(APIView):

    def get(self,request):
        try:
            user=request.user

            if user.is_deleted==True:
                return map_response(message='User does not exist',success=False)
            data= CustomerUserSerializer(user).data
            response_data={
                'user':data
            }

            role= user.role
            profile_mapping={
                user.Role.AGENCY:(AgencyProfile,AgencyProfileSerializer),
                user.Role.PROFESSION:(ProfessionProfile,ProfessionProfileSerializer),
                user.Role.USER:(UserProfile,UserProfileSerializer),
            }


            if role in profile_mapping:
                profile_model, serializer_class= profile_mapping[role]
                try:
                    profile= profile_model.objects.get(user=user)
                    profile_data= serializer_class(profile).data
    
                    if role== user.Role.AGENCY:
                        services= AgencyServices.objects.filter(agency=profile.id)
                        service_serializer= AgencyServicesSerializer(services,many=True).data
                        profile_data['services']=service_serializer
                    
                    elif role==user.Role.PROFESSION:
                        services= ProfessionSelectedService.objects.get(profession= profile.id)
                        service_list=[]
                        for service in services:
                            service_serializer=ProfessionProfileSerializer(service).data
                            service_title= service.service.title
                            service_serializer['service_title']= service_title
                            service_list.append(service_serializer)
                        profile_data['service']= service_list
    
                    if hasattr(profile,'category') and profile.category.title:
                            profile_data['category_title']= profile.category.title
    
                    response_data['profile_data']=profile_data
                except profile_model.DoesNotExist:
                    response_data['profile_data']=None

                return map_response(message='Login Successfull',success=True,data=response_data)
            serializer=CustomerUserSerializer(user).data
            return map_response(message='User Retrieved',success=True,data=serializer.data)
        except Exception as e:
            return map_response(message=str(e),success=False)






















        






    

