from rest_framework.views import APIView
from apps.users.models import *
from apps.users.serializers.auth_serializer import*
from apps.users.serializers.app_profile_serializer import*
from classes.response.map_reponse import map_response
from apps.agency.models import *
from apps.agency.serializers.profile_serializers import*
from classes.extra_schema import extra_schema
from classes.utils import get_value
from django.utils.crypto import get_random_string
from django.conf import settings
import uuid
from django.core.mail import send_mail

class AdminDashboardUserView(APIView):

    def get(self,request):
        if request.user.role=='admin':
            
            try:
                users= CustomUser.objects.all()
                response_data=[]
                for user in users:
                    user_serializer= CustomerUserSerializer(user)
                    if user.role==user.Role.USER:
                        try:
                            user_profile= UserProfile.objects.get(user=user)
                            user_profile_serializer= UserProfileSerializer(user_profile)
                            data={
                                'user':user_serializer.data,
                                f'{user.role} profile':user_profile_serializer.data,
                                
                            }
                        except Exception as e:
                            print(str(e))
                            data={
                                'user':user_serializer.data
                            }
                        response_data.append(data)

                    elif user.role== user.Role.PROFESSION:
                        try:
                            profession_profile=ProfessionProfile.objects.get(user=user)
                            profession_profile_serialzier= ProfessionProfileSerializer(profession_profile)
                            data={
                                'user':user_serializer.data,
                                'profession':profession_profile_serialzier.data
                            }
                        except Exception as e:
                            print(str(e))
                            data={
                                'user':user_serializer.data
                            }
                        response_data.append(data)

                    elif user.role==user.Role.AGENCY:
                        try:
                            agency_profile= AgencyProfile.objects.get(user=user)
                            agency_profile_serializer= AgencyProfileSerializer(agency_profile)
                            data={
                                'user':user_serializer.data,
                                f'{user.role}':agency_profile_serializer.data
                            }
                        except Exception as e:
                            print(str(e))
                            data={
                                'user':user_serializer.data
                            }
                        response_data.append(data)

                return map_response(message='Users Platform',data=response_data,success=True)
            except Exception as e:
                return map_response(message=str(e),success=False)
        else:
            return map_response(message='User must be Admin',success=False)
                            
class AdminDashboardProfessionView(APIView):
    
    def get(self,request):
        # if request.user.role== 'user':
            try:
                profession_profile= CustomUser.objects.all()
                profession_profile_serializer= CustomerUserSerializer(profession_profile,many=True)
                return map_response(message='Profession Users',data=profession_profile_serializer.data,success=True)
            except Exception as e:
                return map_response(message=str(e),success=False)
        # else:
        #     return map_response(message='User must be admin',success=False)


class InviteLinkView(APIView):
    @extra_schema(
        'InviteLink',['email']
    )

    def post(self,request):
        try:
            email= get_value(request,key='email')
            if not email:
                return map_response(message='Email Required',success=False)
            user= CustomUser.objects.filter(email=email)
            if user.exists():
                return map_response(message='This User already exists',success=False)
            
            invite_token= get_random_string(length=32)
            invite_link=f'{settings.FRONTEND_URL}/invite{invite_token}'

            user, created=CustomUser.objects.create(email=email)
            user.qr_code= uuid.uuid4()
            user.qr_code_created_at= timezone.now()
            user.save()

            subject = "You're Invited!"
            message = f"Hello,\n\nYou have been invited to join our platform. Use the following link to register:\n\n{invite_link}\n\nThank you!"
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [email]
            try:
                send_mail(subject,message,from_email,recipient_list)
            except Exception as e:
                return map_response(message=str(e),success=False)
            return map_response(message='Invite Link send succesfully.',data=f'Invite link is{invite_link}',
                                success=True)
        
        except Exception as e:
            return map_response(message=str(e),success=False)
        
    
class AdminDashboardView(APIView):
    def get(self,request):
        try:
            if request.user.role=='admin':
                user_count= CustomUser.objects.count()
                professional_user=CustomUser.objects.filter(role=CustomUser.Role.PROFESSION).count()
                active_user= CustomUser.objects.filter(is_active=True).count()
                agency_user= CustomUser.objects.filter(role=CustomUser.Role.AGENCY).count()
                custom_user=CustomUser.objects.filter(role=CustomUser.Role.USER).count()
                overall_data={
                    'overall_users':user_count,
                    'profession':professional_user,
                    'active_user':active_user,
                    'agency':agency_user,
                    'custom_users':custom_user,
                }

                time_period= 'monthly'
                now= timezone.now()

                filters={}
                if time_period=='monthly':
                    filters={'month':now.month,'year':now.year}
                elif time_period=='yearly':
                    filters={'year':now.year}

                
                #active users
                active_users= CustomUser.objects.filter(
                    is_active=True,
                    last_login_month=filters.get('month',now.month),
                    last_login_year=filters.get('year',now.year)
                ).count()

                new_signup=CustomUser.objects.filter(
                    date_joined_month= filters.get('month',now.month),
                    date_joined_year= filters.get('year',now.year)
                ).count()


                login_activity= CustomUser.objects.filter(
                    last_login_month= filters.get('month',now.month),
                    last_login_year=filters.get('year',now.year)
                )

                monthly_data={
                    'time_period':time_period,
                    'active_users':active_users,
                    'new_signups':new_signup,
                    'login_activity':login_activity,
                }

                data={'monthly_data':monthly_data,'overall_data':overall_data}

                return map_response(message='Dashboard details',data=data,success=True)
            return map_response(message='User must be Admin',success=False)
        except Exception as e:
            return map_response(message=str(e),success=False)





       











