from rest_framework.views import APIView
from apps.agency.models import *
from apps.agency.serializers.profile_serializers import*
from apps.users.models import*
from apps.users.serializers.app_profile_serializer import*
from classes.response.map_reponse import map_response
from classes.extra_schema import extra_schema
from classes.utils import get_value
from classes.response.generic_response import GenericsLC
from rest_framework.pagination import PageNumberPagination



class AgencyDashboardReviewView(APIView):
    def get(self,request,):
        try:
            user=request.user
            agency= AgencyProfile.objects.get(user=user)
            agency_serializer= AgencyProfileSerializer(agency)
            agency_review= AgencyReview.objects.filter(agency=agency)
            response_data=[]

            for review in agency_review:
                user_profile_instance= UserProfile.objects.get(user=review.user)
                user_profile_serializer= UserProfileSerializer(user_profile_instance)

                review_serializer= AgencyReviewSerializer(review)

                review_data={
                    'agency':agency_serializer.data,
                    'user_profile':user_profile_serializer.data,
                    'review':review_serializer.data
                }

                response_data.append(review_data)
            return map_response(message='Agency Review',data=response_data,success=True)
        except Exception as e:
            return map_response(message=str(e),success=False)
        

class AgencyDashboardImagesView(APIView):
    @extra_schema(
        'AgencyIMages',['agency_id','images']
    )

    def post(self,request):
        try:
            agency_id= get_value(request,key='agency_id')
            images= request.getlist('images[]')

            count=0
            for image in images:
                image_data={
                    'images':image,
                    'agency':agency_id
                }

                serializer= AgencyGallerySerializer(data=image_data)
                if serializer.is_valid():
                    return map_response(message=serializer.errors,success=False)
                serializer.save()
                count+=1
            return map_response(message=f'{count} images added',success=False)
        except Exception as e:
            return map_response(message=str(e),success=False)

class GetAgencyDashboardImages(GenericsLC):
    model= AgencyGallery
    serializer_class= AgencyGallerySerializer
    queryset= AgencyGallery.objects.all()

    def get(self,request):
        try:
            user= request.user
            agency= AgencyProfile.objects.get(user=user)
            images= AgencyGallery.objects.filter(agency=agency)
            paginator= PageNumberPagination()
            paginator.page_size=12
            paginated_images= paginator.paginate_queryset(images,request)
            image_serializer= AgencyGallerySerializer(paginated_images,many=True)
            return paginator.get_paginated_response({
                'message':'Got Images',
                'data':image_serializer.data,
                'success':True,
            })
        except Exception as e:
            return map_response(message=str(e),success=False)

class AgencyTeamMembersView(APIView):
    @extra_schema(
        'AgencyDashboard',['agency_id']
    )

    def get(self,request):
        try:
            agency_id= get_value(request,key='agency_id')
            profession= ProfessionProfile.objects.filter(agency=agency_id)

            profession_serializer= ProfessionProfileSerializer(profession, many=True)
            return map_response(message='Team Members',success=True,data=profession_serializer.data)
        except Exception as e:
            return map_response(message=str(e),success=False)
        

class InviteTeamMembersView(APIView):
    @extra_schema(
        'AttachProfession','profession_id'
    )

    def patch(self,request):
        try:
            user=request.user
            profession_id= get_value(request,key='profession_id')
            agency_id= AgencyProfile.objects.get(user=user.id)

            previous_instance_delete= InviteMembers.objects.filter(profession_id=profession_id,agency=agency_id).delete()

            invite_instance= InviteMembers.objects.create(profession_id=profession_id,agency=agency_id)
            profession=ProfessionProfile.objects.get(id=profession_id)
            profession.agency_invite= agency_id
            profession.save()
            self.send_invite_notification(profession,agency_id.id)

            return map_response(message='Invite send',success=True)
        except Exception as e:
            return map_response(message=str(e),success=False)
        

    def send_invite_notification(self,profession,agency_id):
        try:
            profession_owner=profession.user
            agency_name= AgencyProfile.objects.get(id=agency_id).business_name
            notification_message= f' You have been invited by {agency_name}'

            # Notifications.objects.create(user=profession_owner,message=notification_message)
        except Exception as e:
            print(f'failed to send notification to: {str(e)}')

class AcceptRequestView(APIView):
    @extra_schema(
        'AttachPostion',['profession']
    )

    def patch(self,request):
        try:
            data=AgencyEmploye.objects.all()
            print('----->>',data)
            serializer=AgencyEmployeSerializer(data,many=True).data
            print('--->>',serializer)
            user=request.user
            profession_id= get_value(request,key='profession')
            print('----> profession',profession_id)
            agency=AgencyProfile.objects.get(user=user)
            # request_attach= RequestAttach.objects.filter(profession_id=profession_id,agency=agency).first()
            # if not request_attach:
            #     return map_response(message='Request Does not exist',success=False)

            #agency_employe

            agency_employe=AgencyEmploye.objects.filter(agency=agency,profession_id=profession_id).first()
            if agency_employe:
                return map_response(message='Agency Employe already exist',success=False)
            
            agency_employe_instance= AgencyEmploye.objects.create(agency=agency,profession_id=profession_id)

            agency.employee_count+=1
            agency.save()

            # request_attach.request_status=True

            profession_profile=ProfessionProfile.objects.get(id=profession_id)
            profession_profile.agency=agency
            profession_profile.save()
            return map_response(message='Request Accepted',success=True)
        except Exception as e:
            return map_response(message=str(e),success=False)


# will do the settings and this class later once i will have the notification api's setup
# class AgencyDashboardStatsView(APIView):
#     def get(self,request):
#         try:
#             user=request.user
            